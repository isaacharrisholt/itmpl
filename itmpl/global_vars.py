from pathlib import Path

import typer

APP_DIR: Path = Path(typer.get_app_dir("itmpl"))
TEMPLATES_DIR: Path = Path(__file__).parent / "templates"
