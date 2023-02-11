from pathlib import Path

import typer
from rich import print
from typer import Typer

from itmpl import global_vars, templating

app = Typer()


@app.command()
def hello(name: str):
    print(f"Hello {name}")


@app.command()
def new(
    template: str,
    name: str,
    path: Path = Path("."),
    force: bool = typer.Option(False, "--force", "-f"),
):
    template_options = [
        t.name for t in global_vars.TEMPLATES_DIR.iterdir() if t.is_dir()
    ]

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

    templating.render_template(
        project_name=name,
        template=template,
        destination=destination,
        prompt_if_duplicates=not force,
    )

    print(f"Created [green]{template}[/green] project at [green]{destination}[/green]")


if __name__ == "__main__":
    app()
