import importlib.util
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Iterable, List, Tuple

from rich.table import Table

from itmpl.metadata import ItmplToml


def import_external_module(module_path: Path) -> ModuleType:
    """Import a module from an external path."""
    spec = importlib.util.spec_from_file_location("itmpl", module_path)

    if spec is None:
        raise ValueError(f"No module found at path: {module_path}")

    module = importlib.util.module_from_spec(spec)

    if spec.loader is None:
        raise ValueError(f"No loader found for module: {module_path}")

    try:
        spec.loader.exec_module(module)
    except FileNotFoundError:
        raise ValueError(f"No module found at path: {module_path}")

    return module


def construct_table_from_templates(
    templates: Iterable[Tuple[Path, ItmplToml]],
) -> Table:
    """Construct a Rich table from a list of templates."""
    table = Table(show_header=True, header_style="bold")
    table.add_column("Template", justify="left", no_wrap=True, header_style="blue")
    table.add_column("Description")
    table.add_column("Requirements")

    for template, toml_obj in templates:
        table.add_row(
            template.name,
            toml_obj.metadata.template_description,
            ", ".join(toml_obj.metadata.template_requirements),
        )

    return table


def install_dependencies(dependencies: List[str]):
    """Install dependencies."""
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", *dependencies],
    )
