from datetime import datetime
from pathlib import Path
from typing import Dict

import typer

APP_DIR: Path = Path(typer.get_app_dir("itmpl"))

TEMPLATES_DIR: Path = Path(__file__).parent / "templates"

VARIABLES: Dict[str, str] = {
    "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "current_year": datetime.now().strftime("%Y"),
}
