import importlib.util
from pathlib import Path
from types import ModuleType


def import_external_module(module_path: Path) -> ModuleType:
    """Import a module from an external path."""
    spec = importlib.util.spec_from_file_location("itmpl", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module
