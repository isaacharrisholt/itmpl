from pathlib import Path
from typing import Any, Dict, Optional


def get_variables(
    project_name: str,
    destination: Path,
    variables: Dict[str, Any],
) -> Dict[str, Any]:
    raise Exception("This is a test exception")


def post_script(
    project_name: str,
    final_directory: Path,
    variables: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    raise Exception("This is a test exception")
