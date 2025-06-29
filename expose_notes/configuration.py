from pathlib import Path
from typing import List, Dict
from pydantic import BaseModel
import yaml

CONFIGURATION_FILENAME = "config.yaml"

class NoteSource(BaseModel):
    source_id: int
    name: str
    path: str | None = None
    daily_notes: bool = False
    description: str

class DailyNotesConfig(BaseModel):
    enabled: bool = False
    days: int = 60
    paths: List[str] = []

class NotesConfig(BaseModel):
    notes: List[NoteSource]
    vault_path: str = ""
    daily_notes: DailyNotesConfig = DailyNotesConfig()


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


def build_configuration() -> NotesConfig:
    """
    Validate the configuration settings.

    param config: The NotesConfig object to validate.
    """
    config = get_configuration()

    if not config:
        raise ValueError("Configuration not found. Please ensure the config.yaml file is present.")

    vault = Path(config.vault_path)
    if not vault.exists():
        raise ValueError(f"Vault path '{config.vault_path}' does not exist. Please check your configuration.")

    daily_notes = config.daily_notes
    if daily_notes.enabled:
        for path in daily_notes.paths:
            daily_path = vault / path
            if not daily_path.exists():
                raise ValueError(f"Daily notes path '{daily_path}' does not exist. Please check your configuration.")

    return config

def get_note_sources(config: NotesConfig) -> List[NoteSource]:
    """
    Get the list of note sources from the configuration.

    param config: The NotesConfig object containing note sources.
    return: A list of NoteSource objects.
    """
    notes = config.notes

    if config.daily_notes.enabled:
        notes.insert(0, NoteSource(
            source_id=len(notes) + 1,
            name=f"Daily Notes",
            daily_notes=True,
            description=f"My daily notes for the last {config.daily_notes.days} days."
        ))

    return  notes
