import os
import tempfile
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, Optional, Tuple

import jinja2
import typer
from pydantic import ValidationError
from rich import print

from itmpl import config, global_vars, metadata, tree_utils, utils


class DuplicateTemplateError(Exception):
    """Exception raised when there are duplicate templates."""

    def __init__(self, duplicate_templates: Dict[str, Tuple[Path, str]]) -> None:
        super().__init__()
        self.duplicate_templates = duplicate_templates


class IgnoreUndefined(jinja2.Undefined):
    """Ignore undefined variables."""

    def __str__(self):
        if not self._undefined_name:
            return ""
        return "{{ " + self._undefined_name + " }}"


class TemplatingException(Exception):
    """Exception raised when there is an error with the templating."""


def get_templates_in_dir(directory: Path) -> Dict[str, Tuple[Path, str]]:
    """Return a list of templates in a directory with their descriptions."""
    templates = {}
    for path in directory.iterdir():
        if not path.is_dir():
            continue

        meta = metadata.read_itmpl_toml(path / ".itmpl.toml")
        templates[path.name] = (path, meta.metadata.template_description)

    return templates


def get_template_options() -> Dict[str, Tuple[Path, str]]:
    """Return a list of template options and their descriptions."""
    c = config.read_config()
    default_template_options = get_templates_in_dir(global_vars.TEMPLATES_DIR)
    extra_template_options = get_templates_in_dir(c.extra_templates_dir)

    # Find the intersection of the two sets of templates
    duplicate_template_keys = (
        default_template_options.keys() & extra_template_options.keys()
    )
    duplicate_templates = {
        k: v
        for k, v in default_template_options.items()
        if k in duplicate_template_keys
    }

    if duplicate_templates:
        raise DuplicateTemplateError(duplicate_templates)

    return {**default_template_options, **extra_template_options}


def _setup_itmpl_module(directory: Path) -> Optional[ModuleType]:
    """Import the .itmpl.py file in the template directory."""
    itmpl_file = directory / ".itmpl.py"

    if not itmpl_file.exists():
        return None

    try:
        return utils.import_external_module(itmpl_file)
    except Exception as e:
        raise TemplatingException(f"Error when importing .itmpl.py: {e}") from e


def get_default_variables(project_name: str) -> Dict[str, Any]:
    return {
        "project_name": project_name,
        "project_title": project_name.replace("-", " ").replace("_", " ").title(),
    }


def get_toml_variables(temp_directory: Path) -> Dict[str, Any]:
    """Get extra variables from the .itmpl.toml file in the template directory."""
    try:
        meta = metadata.read_itmpl_toml(temp_directory / ".itmpl.toml")
    except ValidationError as e:
        raise TemplatingException(f"Error when validating .itmpl.toml: {e}") from e
    except Exception as e:
        raise TemplatingException(f"Error when reading .itmpl.toml: {e}") from e

    return meta.variables


def get_python_variables(
    temp_directory: Path,
    project_name: str,
    destination: Path,
    variables: Dict[str, Any],
) -> Dict[str, str]:
    """Get extra variables from the .itmpl.py file in the template directory."""
    module = _setup_itmpl_module(temp_directory)

    if not module or not hasattr(module, "get_variables"):
        return {}

    try:
        return module.get_variables(
            project_name,
            destination,
            variables,
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
            project_name,
            final_directory,
            variables,
        )
    except Exception as e:
        raise TemplatingException(
            f"Error when running post script from .itmpl.py: {e}"
        ) from e


def template_directory(
    dir_path: Path,
    variables: Dict[str, Any],
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

            # Ignore .itmpl files
            if file_path.name.startswith(".itmpl"):
                continue

            # Template the file's contents
            try:
                contents_template = jinja2.Template(
                    Path(file_path).read_text(),
                    undefined=(
                        IgnoreUndefined if ignore_undefined else jinja2.StrictUndefined
                    ),
                    keep_trailing_newline=True,
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
    template_path: Path,
    prompt_if_duplicates: bool = True,
):
    default_variables = {
        **get_default_variables(project_name=project_name),
        **global_vars.VARIABLES,
    }

    with tempfile.TemporaryDirectory() as tempdir:
        temp_project_dir = Path(tempdir) / template
        tree_utils.copy_tree(
            template_path,
            temp_project_dir,
        )

        toml_variables = get_toml_variables(temp_project_dir)
        python_variables = get_python_variables(
            temp_directory=temp_project_dir,
            project_name=project_name,
            destination=destination,
            variables={**default_variables, **toml_variables},
        )

        variables = {**default_variables, **toml_variables, **python_variables}
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

        tree_utils.recursive_delete(destination, ".itmpl*")
        tree_utils.recursive_delete(destination, "__pycache__")
