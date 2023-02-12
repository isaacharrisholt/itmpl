from pathlib import Path

from itmpl import metadata


def test_read_itmpl_toml():
    path = Path(__file__).parent / "files" / "test.toml"
    toml = metadata.read_itmpl_toml(path)

    assert toml.metadata.template_description == "Some description"
    assert toml.variables == {"a": 1, "b": 2}


def test_read_itmpl_toml_nonexistent_file():
    path = Path(__file__).parent / "files" / "nonexistent.toml"
    toml = metadata.read_itmpl_toml(path)

    assert toml.metadata.template_description is None
    assert toml.variables == {}
