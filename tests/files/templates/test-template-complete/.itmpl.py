from pathlib import Path
from typing import Any, Dict, Optional

# Variable for testing the template_directory function ignores .itmpl* files:
# {{ project_name }}


def get_variables(
    project_name: str,
    destination: Path,
    variables: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        **variables,
        "project_name": project_name,
        "destination": destination,
        "a": 1,
        "b": 2,
    }


def post_script(
    project_name: str,
    final_directory: Path,
    variables: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    return {
        **variables,
        "project_name": project_name,
        "final_directory": final_directory,
        "a": 1,
        "b": 2,
    }
