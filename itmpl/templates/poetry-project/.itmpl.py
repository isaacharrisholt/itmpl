from pathlib import Path
from typing import Dict

import typer


def get_variables(
    project_name: str,
    destination: Path,
    default_variables: Dict[str, str],
) -> Dict[str, str]:
    project_description = typer.prompt("Project description")
    author = typer.prompt("Project author")
    python_version = typer.prompt("Python version", default="3.11")
    return {
        "project_description": project_description,
        "author": author,
        "python_version": python_version,
    }
