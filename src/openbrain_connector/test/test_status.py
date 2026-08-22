from __future__ import annotations

import pytest
from openbrain_connector.status import ConnectorConfigError, ConnectorState


def _profile() -> dict:
    return {
        "mode": "shadow",
        "identity": {
            "robot_id": "so101-lab-001",
            "release_manifest_sha256": "a" * 64,
            "release_tree_sha256": "b" * 64,
            "checkpoint_sha256": "c" * 64,
            "embodiment_sha256": "d" * 64,
            "observation_spec_sha256": "e" * 64,
            "action_spec_sha256": "f" * 64,
        },
        "topology": {"edge_host": "robot-edge", "inference_host": "inference-host"},
        "raspberry_pi": {"architecture": "aarch64-required"},
        "camera_bindings": {"overview": None, "wrist": None, "capture_ready": False},
        "servo_bus": {
            "controller": None,
            "device": None,
            "discovery_authorized": False,
            "write_commands_enabled": False,
        },
        "hardware_gate": {
            "actuation_authorized": False,
            "motor_commands_authorized": False,
            "physical_estop_verified": False,
            "actuator_gateway_present": False,
        },
        "current_readiness": {"hardware_certified": False},
    }


def _descriptor(profile: dict) -> dict:
    identity = profile["identity"]
    return {
        "schemaVersion": "openkinematics.edge-skill.v1",
        "skill": {
            "id": "so101-vials-to-rack",
            "name": "Vials to rack",
            "version": "20",
            "runtimeStatus": "offline-validated",
        },
        "lineage": {
            "releaseManifestSha256": identity["release_manifest_sha256"],
            "releaseTreeSha256": identity["release_tree_sha256"],
            "checkpointSha256": identity["checkpoint_sha256"],
            "embodimentSha256": identity["embodiment_sha256"],
            "observationSpecSha256": identity["observation_spec_sha256"],
            "actionSpecSha256": identity["action_spec_sha256"],
        },
        "deployment": {
            "robotId": identity["robot_id"],
            "mode": "shadow",
            "actuationAuthorized": False,
            "motorCommandsAuthorized": False,
        },
    }


def test_snapshot_is_explicitly_read_only() -> None:
    profile = _profile()
    snapshot = ConnectorState(profile, _descriptor(profile)).snapshot()

    assert snapshot["runtime"]["mode"] == "shadow"
    assert snapshot["skill"]["shadowOnly"] is True
    assert snapshot["hardware"]["servoWritesEnabled"] is False
    assert snapshot["safety"]["motorCommandsAuthorized"] is False
    assert snapshot["capabilities"] == {
        "status": True,
        "calibration": False,
        "manualControl": False,
        "actuation": False,
    }


def test_accepts_hardware_neutral_edge_runtime_profile() -> None:
    profile = _profile()
    profile["edge_runtime"] = {
        "platform": "custom-arm64",
        "required_architecture": "aarch64",
    }
    del profile["raspberry_pi"]

    snapshot = ConnectorState(profile, _descriptor(profile)).snapshot()

    assert snapshot["runtime"]["requiredArchitecture"] == "aarch64"
    assert snapshot["safety"]["actuationAuthorized"] is False


def test_missing_optional_hardware_sections_stays_fail_closed() -> None:
    profile = _profile()
    del profile["raspberry_pi"]
    del profile["camera_bindings"]
    del profile["servo_bus"]
    del profile["hardware_gate"]
    del profile["current_readiness"]

    snapshot = ConnectorState(profile, _descriptor(profile)).snapshot()

    assert snapshot["runtime"]["requiredArchitecture"] is None
    assert snapshot["hardware"]["servoWritesEnabled"] is False
    assert snapshot["hardware"]["physicalEstopVerified"] is False
    assert snapshot["hardware"]["hardwareCertified"] is False
    assert snapshot["safety"]["motorCommandsAuthorized"] is False


def test_string_booleans_cannot_report_hardware_ready() -> None:
    profile = _profile()
    profile["camera_bindings"]["capture_ready"] = "false"
    profile["hardware_gate"]["physical_estop_verified"] = "false"
    profile["current_readiness"]["hardware_certified"] = "false"

    snapshot = ConnectorState(profile, _descriptor(profile)).snapshot()

    assert snapshot["hardware"]["cameras"]["captureReady"] is False
    assert snapshot["hardware"]["physicalEstopVerified"] is False
    assert snapshot["hardware"]["hardwareCertified"] is False


def test_rejects_unpinned_lineage() -> None:
    profile = _profile()
    descriptor = _descriptor(profile)
    descriptor["lineage"]["checkpointSha256"] = "not-a-sha256"

    with pytest.raises(ConnectorConfigError, match="checkpointSha256"):
        ConnectorState(profile, descriptor)


def test_refuses_open_motor_gate() -> None:
    profile = _profile()
    profile["hardware_gate"]["actuation_authorized"] = True

    with pytest.raises(ConnectorConfigError, match="motor gate"):
        ConnectorState(profile, _descriptor(profile))


def test_refuses_lineage_mismatch() -> None:
    profile = _profile()
    descriptor = _descriptor(profile)
    descriptor["lineage"]["checkpointSha256"] = "f" * 64

    with pytest.raises(ConnectorConfigError, match="checkpointSha256"):
        ConnectorState(profile, descriptor)


def test_applies_only_observational_runtime_state(tmp_path) -> None:
    profile = _profile()
    runtime_path = tmp_path / "runtime.json"
    runtime_path.write_text(
        """{
          "schemaVersion": "openbrain.connector.runtime.v1",
          "inference": {"connected": true, "heartbeatFresh": true},
          "telemetry": {
            "observationSequence": 12,
            "proposalSequence": 11,
            "acceptedProposals": 10,
            "rejectedProposals": 1,
            "lastProposalLatencyMs": 18.5
          },
          "lastDecisionReason": "proposal_accepted_shadow_only",
          "motorCommandsAuthorized": true
        }""",
        encoding="utf-8",
    )

    snapshot = ConnectorState(profile, _descriptor(profile), runtime_path).snapshot()
    assert snapshot["runtime"]["inferenceConnected"] is True
    assert snapshot["telemetry"]["observationSequence"] == 12
    assert snapshot["safety"]["lastDecisionReason"] == "proposal_accepted_shadow_only"
    assert snapshot["safety"]["motorCommandsAuthorized"] is False
