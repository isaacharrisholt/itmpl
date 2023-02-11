from pathlib import Path

import typer
from rich import print
from rich.columns import Columns
from typer import Typer

from itmpl import global_vars, tree_utils

app = Typer()


@app.command()
def hello(name: str):
    print(f"Hello {name}")


@app.command()
def new(
    template: str,
    name: str,
    path: Path = Path("."),
):
    template_options = [
        t.name for t in global_vars.TEMPLATES_DIR.iterdir() if t.is_dir()
    ]

    if template not in template_options:
        columns = Columns(template_options, equal=True, expand=True)
        print(
            f"[red]Template [white]{template}[/white] not found. "
            f"Available templates:[/red]"
        )
        print(columns)
        raise typer.Exit(1)

    duplicates = list(
        tree_utils.find_duplicates(global_vars.TEMPLATES_DIR / template, path / name)
    )

    if duplicates:
        print("[red]The following files already exist and will be overwritten:[/red]")
        for duplicate in duplicates:
            print(f"  {duplicate.resolve()}")

        typer.confirm("Continue?", abort=True)

    tree_utils.copy_tree(
        global_vars.TEMPLATES_DIR / template,
        path / name,
    )


if __name__ == "__main__":
    app()
