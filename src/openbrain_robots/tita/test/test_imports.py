"""The Tita scaffold should at least import cleanly."""


def test_module_importable():
    from openbrain_robots_tita import tita_adapter  # noqa: F401


def test_class_present():
    from openbrain_robots_tita.tita_adapter import TitaAdapter

    assert TitaAdapter.__doc__, "scaffold should explain itself in the docstring"
