"""The G1 scaffold should at least import cleanly."""


def test_module_importable():
    from openbrain_robots_unitree_g1 import unitree_g1_adapter  # noqa: F401


def test_class_present():
    from openbrain_robots_unitree_g1.unitree_g1_adapter import UnitreeG1Adapter

    assert UnitreeG1Adapter.__doc__, "scaffold should explain itself in the docstring"
