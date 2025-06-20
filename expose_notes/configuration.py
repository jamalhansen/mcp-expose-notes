from pathlib import Path
from typing import List, Dict
from pydantic import BaseModel
import yaml

CONFIGURATION_FILENAME = "config.yaml"

class NoteSource(BaseModel):
    source_id: int
    name: str
    path: str
    description: str

class NotesConfig(BaseModel):
    notes: List[NoteSource]


def get_configuration() -> NotesConfig | None:
    """Get configuration settings for the application."""

    if not Path(CONFIGURATION_FILENAME).exists():
        raise FileNotFoundError(f"Configuration file '{CONFIGURATION_FILENAME}' not found.")

    with open(CONFIGURATION_FILENAME, "r") as f:
        yaml_data = yaml.safe_load(f)

    return pydanticize_configuration(yaml_data)

def pydanticize_configuration(yaml_data: Dict) -> NotesConfig:
    """Validate and parse configuration data using Pydantic."""
    return NotesConfig(**yaml_data)