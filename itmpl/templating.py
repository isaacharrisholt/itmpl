import os
import tempfile
from pathlib import Path
from typing import Dict

import jinja2
import typer
from rich import print

from itmpl import global_vars, tree_utils, utils


def get_default_variables(project_name: str) -> Dict[str, str]:
    return {
        "project_name": project_name,
        "project_title": project_name.replace("-", " ").replace("_", " ").title(),
    }


def get_extra_variables(
    temp_directory: Path,
    project_name: str,
    destination: Path,
    default_variables: Dict[str, str],
) -> Dict[str, str]:
    """Get extra variables from the .itmpl.py file in the template directory."""
    itmpl_file = temp_directory / ".itmpl.py"

    if not itmpl_file.exists():
        return {}

    module = utils.import_external_module(itmpl_file)

    if not hasattr(module, "get_variables"):
        return {}

    return module.get_variables(
        project_name=project_name,
        destination=destination,
        default_variables=default_variables,
    )


def template_directory(dir_path: Path, variables: Dict[str, str]) -> None:
    """Template the contents of a directory using Jinja. Both file contents and
    filenames are templated."""
    directories_to_rename = []

    for root, dirs, files in os.walk(dir_path):
        root = Path(root)

        for directory in dirs:
            directories_to_rename.append(root / directory)

        for file in files:
            file_path = root / file

            # Template the file's contents
            try:
                contents_template = jinja2.Template(Path(file_path).read_text())
            except UnicodeDecodeError:
                # Not a unicode file, so skip it
                continue
            rendered = contents_template.render(**variables)
            Path(file_path).write_text(rendered)

            # Rename the file
            filename_template = jinja2.Template(file)
            rendered = filename_template.render(**variables)
            file_path.rename(root / rendered)

    # Rename directories
    # Note: we have to reverse the list of directories to rename because
    # otherwise we might rename a parent directory, and then try to rename its
    # children using an incorrect path.
    for directory in reversed(directories_to_rename):
        root = directory.parent
        dirname_template = jinja2.Template(directory.name)
        rendered = dirname_template.render(**variables)
        directory.rename(root / rendered)


def render_template(
    project_name: str,
    template: str,
    destination: Path,
    prompt_if_duplicates: bool = True,
):
    default_variables = {
        **get_default_variables(project_name=project_name),
        **global_vars.VARIABLES,
    }

    with tempfile.TemporaryDirectory() as tempdir:
        temp_project_dir = Path(tempdir) / template
        tree_utils.copy_tree(
            global_vars.TEMPLATES_DIR / template,
            temp_project_dir,
        )

        extra_variables = get_extra_variables(
            temp_directory=temp_project_dir,
            project_name=project_name,
            destination=destination,
            default_variables=default_variables,
        )

        variables = {**default_variables, **extra_variables}
        template_directory(temp_project_dir, variables)

        duplicates = list(
            tree_utils.find_duplicates(
                temp_project_dir,
                destination,
            ),
        )

        if duplicates and prompt_if_duplicates:
            print(
                "[red]The following files already exist and will be overwritten:[/red]",
            )
            print("\n".join([str(d.resolve()) for d in duplicates]))

            typer.confirm("Continue?", abort=True)

        tree_utils.copy_tree(temp_project_dir, destination)

        tree_utils.reursive_delete(destination, ".itmpl*")
        tree_utils.reursive_delete(destination, "__pycache__")
