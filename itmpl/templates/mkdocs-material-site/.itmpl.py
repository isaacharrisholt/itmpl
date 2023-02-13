import subprocess
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import typer


class DependencyManager(Enum):
    POETRY = "poetry"
    PIP = "pip"
    NONE = "none"


def get_variables(
    project_name: str,
    destination: Path,
    variables: Dict[str, Any],
) -> Dict[str, Any]:
    author_name = typer.prompt("Author name")
    site_url = typer.prompt("Site URL")

    if site_url.endswith("/"):
        site_url = site_url[:-1]

    light_mode_primary_colour = typer.prompt(
        "Light mode primary colour",
        default="#2e69dc",
    ).replace("#", "")
    dark_mode_primary_colour = typer.prompt(
        "Dark mode primary colour",
        default="#19428e",
    ).replace("#", "")
    return {
        "author_name": author_name,
        "site_url": site_url,
        "light_mode_primary_colour": light_mode_primary_colour,
        "dark_mode_primary_colour": dark_mode_primary_colour,
    }


def _add_dependencies_poetry(
    dependencies: List[str],
    final_directory: Path,
) -> None:
    print("Adding Poetry dev dependencies...", end=" ", flush=True)
    subprocess.run(
        [
            "poetry",
            "add",
            "-G",
            "dev",
            *dependencies,
        ],
        cwd=final_directory,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    print("done!")

    # Install dependencies
    print("Installing Poetry dev dependencies...", end=" ", flush=True)
    subprocess.run(
        ["poetry", "install"],
        cwd=final_directory,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    print("done!")


def _add_dependencies_requirements(
    dependencies: List[str],
    pip_path: str,
    final_directory: Path,
) -> None:
    print("Adding dependencies...", end=" ", flush=True)
    subprocess.run(
        [
            pip_path,
            "install",
            *dependencies,
        ],
        cwd=final_directory,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    print("done!")

    docs_requirements_file = final_directory / "requirements.docs.txt"
    dev_requirements_file = final_directory / "requirements.dev.txt"
    requirements_file = final_directory / "requirements.txt"

    if docs_requirements_file.exists():
        print(
            "Adding dev dependencies to requirements.docs.txt...", end=" ", flush=True
        )
        with dev_requirements_file.open("a") as f:
            f.write("\n".join(dependencies))
        print("done!")
    elif dev_requirements_file.exists():
        print("Adding dev dependencies to requirements.dev.txt...", end=" ", flush=True)
        with dev_requirements_file.open("a") as f:
            f.write("\n".join(dependencies))
        print("done!")
    else:
        if not requirements_file.exists():
            requirements_file.touch()

        print("Adding dev dependencies to requirements.txt...", end=" ", flush=True)
        with requirements_file.open("a") as f:
            f.write("\n".join(dependencies))
        print("done!")


def post_script(
    project_name: str,
    final_directory: Path,
    variables: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    # Get pip path
    pip_path = subprocess.run(
        ["which", "pip"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    dependency_method = typer.prompt(
        "How would you like to add dependencies? [pip, poetry, none]",
        type=DependencyManager,
    )

    dependencies = (
        (final_directory / ".itmpl.requirements.dev.txt").read_text().splitlines()
    )

    if dependency_method == DependencyManager.POETRY:
        _add_dependencies_poetry(dependencies, final_directory)
    elif dependency_method == DependencyManager.PIP:
        # Get pip path
        pip_path = subprocess.run(
            ["which", "pip"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        _add_dependencies_requirements(dependencies, pip_path, final_directory)
    elif dependency_method == DependencyManager.NONE:
        print(
            "Skipping dependency installation...\n"
            "You will need to install the following dependencies manually:"
        )
        print("\n".join(dependencies))
    else:
        raise ValueError(f"Unknown dependency method: {dependency_method}")

    return {}
