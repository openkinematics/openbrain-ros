"""Unit tests for the small Joy helpers."""

from openbrain_joystick.joystick_teleop import _axis, _btn
from sensor_msgs.msg import Joy


def _msg(axes, buttons):
    m = Joy()
    m.axes = list(axes)
    m.buttons = list(buttons)
    return m


def test_axis_in_bounds():
    msg = _msg([0.1, 0.2, -0.5], [])
    assert _axis(msg, 0) == 0.1
    assert _axis(msg, 2) == -0.5


def test_axis_out_of_bounds_returns_zero():
    msg = _msg([0.1], [])
    assert _axis(msg, 9) == 0.0
    assert _axis(msg, -1) == 0.0


def test_btn_pressed():
    msg = _msg([], [0, 1, 0])
    assert _btn(msg, 1) is True
    assert _btn(msg, 0) is False


def test_btn_out_of_bounds():
    msg = _msg([], [1])
    assert _btn(msg, 5) is False
