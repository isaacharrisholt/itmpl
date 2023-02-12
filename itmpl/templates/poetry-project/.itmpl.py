import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

import typer
import yaml


def get_variables(
    project_name: str,
    destination: Path,
    variables: Dict[str, Any],
) -> Dict[str, Any]:
    project_description = typer.prompt("Project description")
    project_author = typer.prompt("Project author")
    project_license = typer.prompt("Project license", default="MIT")
    python_version = typer.prompt("Python version", default="3.11")
    return {
        "project_description": project_description,
        "project_author": project_author,
        "project_license": project_license,
        "python_version": python_version,
    }


def _add_dev_dependencies(final_directory: Path) -> None:
    dev_dependencies = final_directory / ".itmpl.requirements.dev.txt"

    if not dev_dependencies.exists():
        return

    print("Adding dev dependencies...", end=" ", flush=True)
    subprocess.run(
        [
            "poetry",
            "add",
            "-G",
            "dev",
            *dev_dependencies.read_text().splitlines(),
        ],
        cwd=final_directory,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    print("done!")


def _add_dependencies(final_directory: Path) -> None:
    dependencies = final_directory / ".itmpl.requirements.txt"

    if not dependencies.exists():
        return

    print("Adding dependencies...", end=" ", flush=True)
    subprocess.run(
        [
            "poetry",
            "add",
            *dependencies.read_text().splitlines(),
        ],
        cwd=final_directory,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    print("done!")


def _get_package_versions(package_names: List[str]) -> Dict[str, str]:
    """Get installed package versions."""
    installed_packages_json = subprocess.run(
        ["pip", "list", "--format=json"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout

    installed_packages = json.loads(installed_packages_json)

    return {
        package["name"]: package["version"]
        for package in installed_packages
        if package["name"] in package_names
    }


def _get_pre_commit_config_package_versions(directory: Path) -> Dict[str, str]:
    """Get package versions from the pre-commit config file."""
    pre_commit_config = directory / ".pre-commit-config.yaml"

    if not pre_commit_config.exists():
        return {}

    with pre_commit_config.open() as f:
        config = yaml.safe_load(f)

    package_names = []

    for repo in config["repos"]:
        for hook in repo["hooks"]:
            package_names.append(hook["name"])

    return _get_package_versions(package_names)


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

    # Deactivate virtual environment
    try:
        subprocess.run(["deactivate"], check=False)
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Check if poetry is installed
    try:
        subprocess.run(["poetry", "--version"], check=True, stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        # Install poetry
        print("Poetry is not installed, installing Poetry...", end=" ", flush=True)
        subprocess.run(
            [pip_path, "install", "poetry"],
            check=True,
            stdout=subprocess.DEVNULL,
        )
        print("done!")

    # Add dependencies
    _add_dependencies(final_directory)
    _add_dev_dependencies(final_directory)

    # Install dependencies
    print("Installing dependencies...", end=" ", flush=True)
    subprocess.run(
        ["poetry", "install"],
        cwd=final_directory,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    print("done!")

    # Get package versions of packages used in pre-commit config
    package_versions = _get_pre_commit_config_package_versions(final_directory)

    # Add package versions to variables
    version_template_strings = {
        f"{package_name}_version": version
        for package_name, version in package_versions.items()
    }
    variables.update(version_template_strings)

    return variables
