from pathlib import Path
from typing import Any, Dict, Optional

import tomli
from pydantic import BaseModel


class ItmplMetadata(BaseModel):
    """Metadata from the .itmpl.toml file."""

    template_description: Optional[str] = None


class ItmplToml(BaseModel):
    """The whole contents of the .itmpl.toml file."""

    metadata: ItmplMetadata = ItmplMetadata()
    variables: Dict[str, Any] = {}


def read_itmpl_toml(path: Path) -> ItmplToml:
    if not path.exists():
        return ItmplToml()
    return ItmplToml.parse_obj(tomli.loads(path.read_text(encoding="utf-8")))
