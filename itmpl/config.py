import enum
from pathlib import Path

import typer
from pydantic import BaseModel
from pydantic.fields import ModelField
from rich import print
from typer import Typer

from itmpl.global_vars import APP_DIR

app = Typer()


CONFIG_PATH = APP_DIR / "config.json"


class Config(BaseModel):
    """Configuration for iTmpl."""

    extra_templates_dir: Path = APP_DIR / "templates"


ConfigOption = enum.Enum("ConfigOption", {k: k for k in Config.__fields__})


def read_config() -> Config:
    if not CONFIG_PATH.exists():
        return Config()
    return Config.parse_file(CONFIG_PATH)


def write_config(config: Config):
    with CONFIG_PATH.open("w") as f:
        f.write(config.json())


@app.command("show")
def show(option: ConfigOption = typer.Argument(None)):  # type: ignore
    """Show the current configuration."""
    config = read_config()
    if option:
        print(config.__getattribute__(option.value))
        return

    print(config.json(indent=4))


@app.command("set")
def set_(
    option: ConfigOption,  # type: ignore
    value: str,
):
    """Set a configuration option."""
    config = read_config()

    # Some custom validation using Pydantic's ModelField validation
    model_field: ModelField = config.__fields__[option.value]
    other_attrs = {k: v for k, v in config.__dict__.items() if k != option.value}
    new, error = model_field.validate(value, other_attrs, loc=option.value, cls=Config)

    if error:
        raise typer.BadParameter(
            f"{value} is not a valid {model_field.type_.__name__}",
            param_hint=option.value,
        )

    if new and model_field.type_ == Path and not (new.exists() and new.is_dir()):
        raise typer.BadParameter(
            f"{value} is not a valid directory",
            param_hint=option.value,
        )

    config.__setattr__(option.value, new)
    write_config(config)

    print(f"Set [green]{option.value}[/green] to [green]{new}[/green]")


@app.command()
def get(option: ConfigOption):  # type: ignore
    """Get a configuration option."""
    config = read_config()
    print(
        f"[green]{option.value}[/green] is set to "
        f"[green]{config.__getattribute__(option.value)}[/green]"
    )


@app.command()
def reset():
    """Reset the configuration to the default values."""
    typer.confirm("Are you sure you want to reset the configuration?", abort=True)
    write_config(Config())
    print("Reset configuration to default values.")
