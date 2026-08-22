from __future__ import annotations

import json
import platform
import re
import socket
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CONNECTOR_SCHEMA_VERSION = "openbrain.connector.status.v1"
DESCRIPTOR_SCHEMA_VERSION = "openkinematics.edge-skill.v1"
_SHA256 = re.compile(r"^[a-f0-9]{64}$")


class ConnectorConfigError(ValueError):
    """Raised when the connector inputs could accidentally widen authority."""


class ConnectorState:
    """Immutable boot configuration plus read-only runtime counters.

    There is intentionally no actuator object and no command method in this
    package. Runtime integrations may replace the telemetry snapshot later,
    but the HTTP surface remains observational.
    """

    def __init__(
        self,
        hardware_profile: dict[str, Any],
        skill_descriptor: dict[str, Any],
        runtime_state_path: str | Path | None = None,
    ) -> None:
        self._profile = deepcopy(hardware_profile)
        self._descriptor = deepcopy(skill_descriptor)
        self._runtime_state_path = Path(runtime_state_path) if runtime_state_path else None
        self._validate()

    @classmethod
    def from_files(
        cls,
        hardware_profile: str | Path,
        skill_descriptor: str | Path,
        runtime_state_path: str | Path | None = None,
    ):
        return cls(
            _read_json(hardware_profile),
            _read_json(skill_descriptor),
            runtime_state_path,
        )

    def snapshot(self) -> dict[str, Any]:
        profile = self._profile
        descriptor = self._descriptor
        identity = profile["identity"]
        topology = profile["topology"]
        edge = _edge_runtime(profile)
        cameras = _optional_mapping(profile, "camera_bindings")
        servo = _optional_mapping(profile, "servo_bus")
        gate = _optional_mapping(profile, "hardware_gate")
        readiness = _optional_mapping(profile, "current_readiness")
        skill = descriptor["skill"]
        lineage = descriptor["lineage"]

        result = {
            "schemaVersion": CONNECTOR_SCHEMA_VERSION,
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "robot": {
                "id": identity["robot_id"],
                "name": identity.get("robot_name") or identity["robot_id"],
            },
            "runtime": {
                "mode": profile["mode"],
                "edgeHost": _configured_or_actual(topology.get("edge_host"), socket.gethostname()),
                "edgeArchitecture": platform.machine() or "unknown",
                "requiredArchitecture": edge.get("required_architecture")
                or edge.get("architecture"),
                "inferenceHost": topology.get("inference_host") or "not configured",
                "inferenceConnected": False,
                "heartbeatFresh": False,
            },
            "skill": {
                "id": skill["id"],
                "name": skill["name"],
                "version": skill["version"],
                "runtimeStatus": skill["runtimeStatus"],
                "checkpointSha256": lineage["checkpointSha256"],
                "releaseManifestSha256": lineage["releaseManifestSha256"],
                "observationSpecSha256": lineage["observationSpecSha256"],
                "actionSpecSha256": lineage["actionSpecSha256"],
                "shadowOnly": True,
            },
            "hardware": {
                "cameras": {
                    "overview": _nullable_string(cameras.get("overview")),
                    "wrist": _nullable_string(cameras.get("wrist")),
                    "captureReady": cameras.get("capture_ready") is True,
                },
                "servoController": _nullable_string(servo.get("controller")),
                "servoDevice": _nullable_string(servo.get("device")),
                "servoDiscoveryAuthorized": servo.get("discovery_authorized") is True,
                "servoWritesEnabled": False,
                "physicalEstopVerified": gate.get("physical_estop_verified") is True,
                "actuatorGatewayPresent": gate.get("actuator_gateway_present") is True,
                "hardwareCertified": readiness.get("hardware_certified") is True,
            },
            "safety": {
                "actuationAuthorized": False,
                "motorCommandsAuthorized": False,
                "lastDecisionReason": "connector_started_read_only",
            },
            "telemetry": {
                "observationSequence": None,
                "proposalSequence": None,
                "acceptedProposals": 0,
                "rejectedProposals": 0,
                "lastProposalLatencyMs": None,
            },
            "capabilities": {
                "status": True,
                "calibration": False,
                "manualControl": False,
                "actuation": False,
            },
        }
        self._apply_runtime_state(result)
        return result

    def _apply_runtime_state(self, result: dict[str, Any]) -> None:
        if self._runtime_state_path is None or not self._runtime_state_path.exists():
            return
        try:
            state = _read_json(self._runtime_state_path)
            if state.get("schemaVersion") != "openbrain.connector.runtime.v1":
                raise ConnectorConfigError("unsupported runtime state schema")
            inference = _required_mapping(state, "inference")
            connected = _required_bool(inference, "connected")
            heartbeat_fresh = _required_bool(inference, "heartbeatFresh")
            telemetry = _required_mapping(state, "telemetry")
            checked_telemetry = {
                "observationSequence": _nullable_nonnegative_int(telemetry, "observationSequence"),
                "proposalSequence": _nullable_nonnegative_int(telemetry, "proposalSequence"),
                "acceptedProposals": _nonnegative_int(telemetry, "acceptedProposals"),
                "rejectedProposals": _nonnegative_int(telemetry, "rejectedProposals"),
                "lastProposalLatencyMs": _nullable_nonnegative_number(
                    telemetry, "lastProposalLatencyMs"
                ),
            }
            reason = state.get("lastDecisionReason")
            if not isinstance(reason, str) or not reason:
                raise ConnectorConfigError("runtime state lastDecisionReason is invalid")
        except (ConnectorConfigError, OSError, json.JSONDecodeError):
            result["runtime"]["inferenceConnected"] = False
            result["runtime"]["heartbeatFresh"] = False
            result["safety"]["lastDecisionReason"] = "runtime_state_invalid"
            return
        result["runtime"]["inferenceConnected"] = connected
        result["runtime"]["heartbeatFresh"] = heartbeat_fresh
        result["telemetry"] = checked_telemetry
        result["safety"]["lastDecisionReason"] = reason

    def _validate(self) -> None:
        profile = self._profile
        descriptor = self._descriptor
        if profile.get("mode") != "shadow":
            raise ConnectorConfigError("v1 connector requires a shadow hardware profile")
        if descriptor.get("schemaVersion") != DESCRIPTOR_SCHEMA_VERSION:
            raise ConnectorConfigError("unsupported edge skill descriptor schema")
        for section in ("identity", "topology"):
            if not isinstance(profile.get(section), dict):
                raise ConnectorConfigError(f"hardware profile section is missing: {section}")
        identity = profile["identity"]
        topology = profile["topology"]
        _required_nonempty_string(identity, "robot_id", "hardware profile identity")
        for key in ("edge_host", "inference_host"):
            value = topology.get(key)
            if value is not None and not isinstance(value, str):
                raise ConnectorConfigError(f"hardware profile topology {key} is invalid")
        edge = _edge_runtime(profile)
        for key in ("camera_bindings", "servo_bus", "hardware_gate", "current_readiness"):
            _optional_mapping(profile, key)
        required_architecture = edge.get("required_architecture") or edge.get("architecture")
        if required_architecture is not None and not isinstance(required_architecture, str):
            raise ConnectorConfigError("edge runtime architecture must be a string or null")
        skill = descriptor.get("skill")
        if not isinstance(skill, dict):
            raise ConnectorConfigError("skill descriptor skill section is missing")
        for key in ("id", "name", "version", "runtimeStatus"):
            _required_nonempty_string(skill, key, "skill descriptor")
        servo = _optional_mapping(profile, "servo_bus")
        gate = _optional_mapping(profile, "hardware_gate")
        if any(
            (
                servo.get("write_commands_enabled"),
                gate.get("actuation_authorized"),
                gate.get("motor_commands_authorized"),
            )
        ):
            raise ConnectorConfigError("read-only connector refuses an open motor gate")
        deployment = descriptor.get("deployment")
        if not isinstance(deployment, dict) or any(
            (
                deployment.get("actuationAuthorized"),
                deployment.get("motorCommandsAuthorized"),
            )
        ):
            raise ConnectorConfigError("skill descriptor requests actuator authority")
        if deployment.get("robotId") != profile["identity"].get("robot_id"):
            raise ConnectorConfigError("skill descriptor robot identity mismatch")
        lineage = descriptor.get("lineage")
        if not isinstance(lineage, dict):
            raise ConnectorConfigError("skill descriptor lineage is missing")
        expected = {
            "releaseManifestSha256": "release_manifest_sha256",
            "checkpointSha256": "checkpoint_sha256",
            "observationSpecSha256": "observation_spec_sha256",
            "actionSpecSha256": "action_spec_sha256",
        }
        for descriptor_key, profile_key in expected.items():
            descriptor_value = lineage.get(descriptor_key)
            profile_value = profile["identity"].get(profile_key)
            if (
                not isinstance(descriptor_value, str)
                or not _SHA256.fullmatch(descriptor_value)
                or descriptor_value != profile_value
            ):
                raise ConnectorConfigError(f"skill descriptor lineage mismatch: {descriptor_key}")


def _read_json(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ConnectorConfigError(f"expected JSON object: {path}")
    return value


def _configured_or_actual(configured: Any, actual: str) -> str:
    if isinstance(configured, str) and configured and "required" not in configured:
        return configured
    return actual


def _nullable_string(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None


def _required_nonempty_string(value: dict[str, Any], key: str, section: str) -> str:
    result = value.get(key)
    if not isinstance(result, str) or not result:
        raise ConnectorConfigError(f"{section} string is invalid: {key}")
    return result


def _edge_runtime(profile: dict[str, Any]) -> dict[str, Any]:
    """Return the hardware-neutral edge section, accepting the legacy v1 profile.

    Profiles may omit this section entirely when the actual hostname and
    architecture are sufficient. Missing values narrow information only; they
    never widen connector authority.
    """

    if "edge_runtime" in profile:
        edge = profile["edge_runtime"]
        if not isinstance(edge, dict):
            raise ConnectorConfigError("hardware profile section is invalid: edge_runtime")
        return edge
    if "raspberry_pi" in profile:
        legacy = profile["raspberry_pi"]
        if not isinstance(legacy, dict):
            raise ConnectorConfigError("hardware profile section is invalid: raspberry_pi")
        return legacy
    return {}


def _optional_mapping(value: dict[str, Any], key: str) -> dict[str, Any]:
    result = value.get(key)
    if result is None:
        return {}
    if not isinstance(result, dict):
        raise ConnectorConfigError(f"hardware profile section is invalid: {key}")
    return result


def _required_mapping(value: dict[str, Any], key: str) -> dict[str, Any]:
    result = value.get(key)
    if not isinstance(result, dict):
        raise ConnectorConfigError(f"runtime state section is missing: {key}")
    return result


def _required_bool(value: dict[str, Any], key: str) -> bool:
    result = value.get(key)
    if not isinstance(result, bool):
        raise ConnectorConfigError(f"runtime state boolean is invalid: {key}")
    return result


def _nonnegative_int(value: dict[str, Any], key: str) -> int:
    result = value.get(key)
    if not isinstance(result, int) or isinstance(result, bool) or result < 0:
        raise ConnectorConfigError(f"runtime state integer is invalid: {key}")
    return result


def _nullable_nonnegative_int(value: dict[str, Any], key: str) -> int | None:
    result = value.get(key)
    if result is None:
        return None
    return _nonnegative_int(value, key)


def _nullable_nonnegative_number(value: dict[str, Any], key: str) -> float | int | None:
    result = value.get(key)
    if result is None:
        return None
    # Tuple form keeps this library importable on Python 3.9 edge hosts.
    if isinstance(result, bool) or not isinstance(result, (float, int)) or result < 0:  # noqa: UP038
        raise ConnectorConfigError(f"runtime state number is invalid: {key}")
    return result
