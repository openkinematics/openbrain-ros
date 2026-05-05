"""Unit tests for the pure-Python check helpers."""

import json

from openbrain_diagnostics.checks import (
    CHECKS,
    CheckResult,
    Severity,
    check_disk_space,
    check_network_route,
    check_ros_env,
    run_all_checks,
    to_json,
)


def test_severity_ordering():
    assert Severity.OK < Severity.WARN < Severity.ERROR


def test_run_all_returns_one_per_check():
    results = run_all_checks()
    assert len(results) == len(CHECKS)
    assert all(isinstance(r, CheckResult) for r in results)


def test_disk_check_reports_a_message():
    r = check_disk_space()
    assert isinstance(r.message, str) and r.message
    assert "free_bytes" in r.details or r.severity == Severity.ERROR


def test_network_check_returns_severity():
    r = check_network_route()
    assert isinstance(r.severity, Severity)


def test_ros_env_check_runs():
    r = check_ros_env()
    assert r.name == "ros_env"


def test_to_json_round_trips():
    results = [
        CheckResult("foo", Severity.OK, "all good", {"k": "v"}),
        CheckResult("bar", Severity.ERROR, "broken", {}),
    ]
    parsed = json.loads(to_json(results))
    assert parsed[0]["severity"] == "OK"
    assert parsed[1]["severity"] == "ERROR"
    assert parsed[0]["details"]["k"] == "v"
