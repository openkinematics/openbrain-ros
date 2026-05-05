"""Sanity checks on the psutil fallback path."""

from openbrain_demos_health.health_node import _all_temps, _first_temp


def test_first_temp_returns_nan_or_float():
    val = _first_temp(["__definitely_not_a_real_sensor__"])
    assert val != val or isinstance(val, float)  # NaN sentinel or finite


def test_all_temps_returns_list():
    zones = _all_temps()
    assert isinstance(zones, list)
