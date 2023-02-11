import os
import tempfile
from pathlib import Path
from types import ModuleType
from typing import Dict, Optional

import jinja2
import typer
from itmpl import global_vars, tree_utils, utils
from rich import print

ITMPL_MODULE: Optional[ModuleType] = None


class IgnoreUndefined(jinja2.Undefined):
    """Ignore undefined variables."""

    def __str__(self):
        return "{{ " + self._undefined_name + " }}"


class TemplatingException(Exception):
    """Exception raised when there is an error with the templating."""


def _setup_itmpl_module(directory: Path) -> Optional[ModuleType]:
    """Import the .itmpl.py file in the template directory."""
    global ITMPL_MODULE

    if ITMPL_MODULE is not None:
        return ITMPL_MODULE

    itmpl_file = directory / ".itmpl.py"

    if not itmpl_file.exists():
        return None

    ITMPL_MODULE = utils.import_external_module(itmpl_file)

    return ITMPL_MODULE


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
    module = _setup_itmpl_module(temp_directory)

    if not module or not hasattr(module, "get_variables"):
        return {}

    try:
        return module.get_variables(
            project_name=project_name,
            destination=destination,
            default_variables=default_variables,
        )
    except Exception as e:
        raise TemplatingException(
            f"Error when getting extra variables from .itmpl.py: {e}"
        ) from e


def run_post_script(
    project_name: str,
    final_directory: Path,
    variables: Dict[str, str],
) -> Dict[str, str]:
    """Run the post script in the .itmpl.py file in the template directory."""
    module = _setup_itmpl_module(final_directory)

    if not module or not hasattr(module, "post_script"):
        return {}

    try:
        return module.post_script(
            project_name=project_name,
            final_directory=final_directory,
            variables=variables,
        )
    except Exception as e:
        raise TemplatingException(
            f"Error when running post script from .itmpl.py: {e}"
        ) from e


def template_directory(
    dir_path: Path,
    variables: Dict[str, str],
    ignore_undefined: bool = False,
) -> None:
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
                contents_template = jinja2.Template(
                    Path(file_path).read_text(),
                    undefined=(
                        IgnoreUndefined if ignore_undefined else jinja2.StrictUndefined
                    ),
                )
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
            default_variables=default_variables.copy(),
        )

        variables = {**default_variables, **extra_variables}
        template_directory(temp_project_dir, variables, ignore_undefined=True)

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
        new_variables = run_post_script(
            project_name=project_name,
            final_directory=destination,
            variables=variables.copy(),
        )

        # If the post script returns new variables, template the directory again with
        # the new variables. This time, we don't ignore undefined variables, so that
        # any extraneous Jinja is ignored.
        if new_variables:
            try:
                template_directory(destination, new_variables, ignore_undefined=False)
            except jinja2.exceptions.UndefinedError as e:
                raise TemplatingException(
                    f"Error when templating directory: {e}"
                ) from e

        tree_utils.reursive_delete(destination, ".itmpl*")
        tree_utils.reursive_delete(destination, "__pycache__")
