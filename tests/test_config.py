from pathlib import Path

from typer.testing import CliRunner

from itmpl import config, global_vars

runner = CliRunner()


def test_read_config_no_config(monkeypatch):
    monkeypatch.setattr(
        config,
        "CONFIG_PATH",
        Path(__file__).parent / "files" / "nonexistent_config.json",
    )
    c = config.read_config()
    assert c.extra_templates_dir == global_vars.APP_DIR / "templates"


def test_read_config(monkeypatch, mock_config_file):
    monkeypatch.setattr(
        config,
        "CONFIG_PATH",
        mock_config_file,
    )
    c = config.read_config()
    assert c.extra_templates_dir == Path("/tmp/templates")


def test_set_invalid_option():
    result = runner.invoke(config.app, ["set", "invalid_option", "value"])
    assert result.exit_code == 2


def test_set_extra_templates_dir(monkeypatch, mock_config_file):
    c = config.read_config()
    assert c.extra_templates_dir == Path("/tmp/templates")

    Path("/tmp/templates_after").mkdir(parents=True, exist_ok=True)
    result = runner.invoke(
        config.app,
        ["set", "extra_templates_dir", "/tmp/templates_after"],
    )
    assert result.exit_code == 0

    c = config.read_config()

    assert c.extra_templates_dir == Path("/tmp/templates_after")


def test_set_extra_templates_dir_invalid_directory(monkeypatch, mock_config_file):
    c = config.read_config()
    assert c.extra_templates_dir == Path("/tmp/templates")

    result = runner.invoke(
        config.app,
        ["set", "extra_templates_dir", "not_a_directory"],
    )
    assert result.exit_code == 2

    c = config.read_config()
    assert c.extra_templates_dir == Path("/tmp/templates")


def test_reset_config(monkeypatch, mock_config_file):
    c = config.read_config()
    assert c.extra_templates_dir == Path("/tmp/templates")

    Path("/tmp/templates_after").mkdir(parents=True, exist_ok=True)
    result = runner.invoke(
        config.app,
        ["set", "extra_templates_dir", "/tmp/templates_after"],
    )
    assert result.exit_code == 0

    c = config.read_config()
    assert c.extra_templates_dir == Path("/tmp/templates_after")

    result = runner.invoke(config.app, ["reset"], input="y\n")
    assert result.exit_code == 0

    c = config.read_config()
    assert c.extra_templates_dir == global_vars.APP_DIR / "templates"
