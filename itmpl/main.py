import subprocess
from pathlib import Path
from typing import Optional

import typer
from rich import print
from typer import Typer

from itmpl import config, global_vars, templating, utils

app = Typer()
app.add_typer(config.app, name="config", help="Manage iTmpl configuration.")


@app.command("list")
def list_():
    """List all available templates."""
    print(
        utils.construct_table_from_templates(
            templating.get_template_options().values(),
        ),
    )


@app.command()
def new(
    template: str,
    name: str,
    path: Path = typer.Option(
        Path("."),
        "--path",
        "-p",
        exists=True,
        help="The path to create the project in.",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite any files that already exist without prompting.",
    ),
):
    """Create a new project from a template.

    Parameters
    ----------
    template : str
        The name of the template to use.
    name : str
        The name of the project to create.
    path : Path
        The path to create the project in.
    force : bool
        If True, overwrite any files that already exist without prompting.
    """
    try:
        template_options = templating.get_template_options()
    except templating.DuplicateTemplateError as e:
        print("[red]Duplicate templates found:[/red]")
        print(utils.construct_table_from_templates(e.duplicate_templates.values()))
        print("[red]Please remove the duplicates and try again.[/red]")
        raise typer.Exit(1)

    if template not in template_options:
        print(
            f"[red]Template [white]{template}[/white] not found. "
            f"Available templates:[/red]"
        )
        print(utils.construct_table_from_templates(template_options.values()))
        raise typer.Exit(1)

    # Allow the user to template in this directory
    path = path.resolve()
    if path.name == name:
        path = path.parent

    destination = path / name

    template_path = template_options[template][0]

    try:
        templating.render_template(
            project_name=name,
            template=template,
            destination=destination,
            template_path=template_path,
            prompt_if_duplicates=not force,
        )
    except templating.TemplatingException as e:
        print(f"[red]Error when templating project:[/red] {e}")
        raise typer.Exit(1)

    print(f"Created [green]{template}[/green] project at [green]{destination}[/green]")


@app.command()
def deps(template: Optional[str] = typer.Argument(None)):
    """Install dependencies for the specified template. If no template is specified,
    install dependencies for all templates."""
    try:
        template_options = templating.get_template_options()
    except templating.DuplicateTemplateError as e:
        print("[red]Duplicate templates found:[/red]")
        print(utils.construct_table_from_templates(e.duplicate_templates.values()))
        print("[red]Please remove the duplicates and try again.[/red]")
        raise typer.Exit(1)

    if template is not None and template not in template_options:
        print(
            f"[red]Template [white]{template}[/white] not found. "
            f"Available templates:[/red]"
        )
        print(utils.construct_table_from_templates(template_options.values()))
        raise typer.Exit(1)

    if template is None:
        templates_with_dependencies = [
            (template_name, dependencies)
            for template_name, (_, _, dependencies) in template_options.items()
        ]
    else:
        templates_with_dependencies = [(template, template_options[template][2])]

    to_install = [
        (template_name, dependencies)
        for template_name, dependencies in templates_with_dependencies
        if dependencies
    ]

    if not to_install:
        print("[green]No dependencies to install.[/green]")
        raise typer.Exit(0)

    for template_name, dependencies in to_install:
        print(
            f"[green]Installing dependencies for template "
            f"[white]{template_name}[/white][/green]"
        )
        try:
            utils.install_dependencies(dependencies)
        except subprocess.CalledProcessError as e:
            print(
                f"[red]Error installing dependencies for template "
                f"[white]{template_name}[/white]: {e}[/red]"
            )

    print("[green]Done.[/green]")


@app.callback()
def create_directories():
    """Create directories used by iTmpl. This is called automatically when iTmpl is
    run."""
    global_vars.APP_DIR.mkdir(parents=True, exist_ok=True)
    global_vars.TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    c = config.read_config()
    c.extra_templates_dir.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    app()
