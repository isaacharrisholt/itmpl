import json
import tempfile
from pathlib import Path

import pytest
from itmpl import config


@pytest.fixture
def mock_config_file(monkeypatch):
    path = Path(__file__).parent / "files" / "config.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()

    with path.open("w") as f:
        json.dump({"extra_templates_dir": "/tmp/templates"}, f)

    monkeypatch.setattr(
        config,
        "CONFIG_PATH",
        path,
    )

    yield path
    path.unlink()


@pytest.fixture
def template_dirs():
    """Create a temporary directory for the test to use."""
    source = Path(__file__).parent / "files" / "templates"
    with tempfile.TemporaryDirectory() as tempdir:
        path = Path(tempdir)
        destination = path / "destination"
        destination.mkdir()

        yield source, destination


@pytest.fixture
def tempdir():
    """Create a temporary directory for the test to use."""
    with tempfile.TemporaryDirectory() as tempdir:
        path = Path(tempdir)
        source = path / "source"
        destination = path / "destination"
        source.mkdir()
        destination.mkdir()

        yield path, source, destination
