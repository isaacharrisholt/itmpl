from pathlib import Path

import typer
from rich import print
from typer import Typer

from itmpl import config, global_vars, templating

app = Typer()
app.add_typer(config.app, name="config")


@app.command()
def new(
    template: str,
    name: str,
    path: Path = Path("."),
    force: bool = typer.Option(False, "--force", "-f"),
):
    c = config.read_config()
    default_template_options = {
        t.name for t in global_vars.TEMPLATES_DIR.iterdir() if t.is_dir()
    }
    extra_template_options = {
        t.name for t in c.extra_templates_dir.iterdir() if t.is_dir()
    }

    duplicate_templates = default_template_options.intersection(extra_template_options)
    if duplicate_templates:
        print("[red]Duplicate templates found:[/red]")
        print("\n".join(duplicate_templates))
        print("[red]Please remove the duplicates and try again.[/red]")
        raise typer.Exit(1)

    template_options = default_template_options.union(extra_template_options)

    if template not in template_options:
        print(
            f"[red]Template [white]{template}[/white] not found. "
            f"Available templates:[/red]"
        )
        print("\n".join(template_options))
        raise typer.Exit(1)

    # Allow the user to template in this directory
    if path.name == name:
        path = path.parent

    destination = path / name

    try:
        templating.render_template(
            project_name=name,
            template=template,
            destination=destination,
            prompt_if_duplicates=not force,
        )
    except templating.TemplatingException as e:
        print(f"[red]Error when templating project:[/red] {e}")
        raise typer.Exit(1)

    print(f"Created [green]{template}[/green] project at [green]{destination}[/green]")


@app.callback()
def create_directories():
    global_vars.APP_DIR.mkdir(parents=True, exist_ok=True)
    global_vars.TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    c = config.read_config()
    c.extra_templates_dir.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    app()
