from pathlib import Path
from typing import List
import json

import frontmatter
from mcp.server.fastmcp import FastMCP
from expose_notes.configuration import NoteSource, NotesConfig, build_configuration, get_note_sources
from expose_notes.frontmatter_reader import NoteSet, Note, build_note_set_for_source
from datetime import datetime, timedelta

mcp = FastMCP("Expose Notes Scanner", "expose_notes")

config = build_configuration()
notes = get_note_sources(config)
vault = Path(config.vault_path)

def build_daily_note_set(daily_notes_config, vault_path: Path) -> NoteSet | None:
    """
    Build a note set for daily notes based on the configuration.

    param daily_notes_config: The configuration for daily notes.
    param vault_path: The path to the vault directory.
    return: A NoteSet object containing daily notes, or None if not enabled.
    """
    if not daily_notes_config.enabled:
        return None

    notes = []
    for days_ago in range(daily_notes_config.days):
        for raw_path in daily_notes_config.paths:
            base_path = Path(raw_path)

            note_date = (datetime.now() - timedelta(days=days_ago))
            filename = note_date.strftime("%Y-%m-%d")
            note_path = base_path / f"{filename}.md"
            daily_note_path = vault_path / note_path

            if not daily_note_path.exists():
                continue

            with open(daily_note_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)

            note = Note(
                note_id=days_ago + 1,
                path=str(note_path),
                title="Daily Note for " + filename,
                created=note_date.isoformat(),
                description="A daily written update that captures thoughts, events, and reflections for the day."
            )

            notes.append(note)
        

    note_set = NoteSet(
        generated_by="expose_notes",
        generated_on=datetime.now().isoformat(),
        daily_notes=True,
        total_files=len(notes),
        notes=notes
    )

    return note_set

def get_note_sets(config: NotesConfig, notes_sources: List[NoteSource]) -> List[NoteSet]:
    """
    Build a list of note sets from the configuration and note sources.

    param config: The NotesConfig object containing configuration settings.
    param notes: A list of NoteSource objects.
    return: A list of NoteSet objects.
    """
    if not config or not notes:
        return []

    note_sets = []
    
    for note in notes_sources:
        if note.daily_notes:
            note_set = build_daily_note_set(config.daily_notes, Path(config.vault_path))

            if note_set:
                note_sets.append(note_set)
        else:
            path = vault / note.path if note.path else vault
            
            note_set = build_note_set_for_source(path)
            if note_set:
                note_sets.append(note_set)

    return note_sets

note_sets = get_note_sets(config, notes)

@mcp.tool()
def get_note_source_list() -> List[NoteSource]:
    """
    Get the list of note sources from the configuration.

    return: A list of NoteSource objects.
    """
    return notes

def get_note_source(source_id: int) -> NoteSource | None:
    """
    Get a specific note source by ID.

    param source_id: The ID of the note source.
    return: The NoteSource object if found, otherwise None.
    """
    for note in notes:
        if note.source_id == source_id:
            return note
    return None

@mcp.tool()
def get_note_set(source_id: int) -> NoteSet:
    """
    Get a specific note set by ID.

    param source_id: The ID of the note source.
    return: The NoteSetList object if found, otherwise None.
    """
    source = get_note_source(source_id)

    if not source:
        raise ValueError(f"Note source with ID {source_id} not found.")
    
    if source.daily_notes:
        for note_set in note_sets:
            if note_set.daily_notes:
                return note_set
    
    if not source.path:
        raise ValueError(f"Note source with ID {source_id} does not have a valid path.")
    
    path = vault / source.path

    if not path.exists():
        raise ValueError(f"Note source path '{source.path}' does not exist in the vault.")
    
    for note_set in note_sets:
        if note_set.daily_notes:
            continue

        if not note_set.directory:
            raise ValueError(f"Note source with ID {source_id} does not have a directory set.")
        note_set_path = Path(note_set.directory)
        if note_set_path == path:
            return note_set
            
    raise ValueError(f"Note set not found for source ID {source_id} with path '{path}'.")

def get_note(source_id: int, note_id: int) -> Note:
    """
    Get a specific note by source ID and note ID.

    param source_id: The ID of the note source.
    param note_id: The ID of the note set.
    return: The NoteSet object if found, otherwise None.
    """
    note_set = get_note_set(source_id)

    if not note_set:
        raise ValueError(f"Note set not found for source ID {source_id}.")

    for note_set in note_set.notes:
        if note_set.note_id == note_id:
            return note_set
    
    raise ValueError(f"Note with ID {note_id} not found in note set for source ID {source_id}.")

@mcp.tool()
def get_note_text(source_id: int, note_id: int) -> str | None:
    """
    Get a specific note by source ID and note ID.

    param source_id: The ID of the note source.
    param note_id: The ID of the note.
    return: The text of the note.
    """
    note = get_note(source_id, note_id)

    if not note:
        raise ValueError(f"Note set not found for source ID {source_id} and note ID {note_id}.")

    if not note.path:
        raise ValueError(f"Note path is not set for note ID {note_id}.")
    
    note_path = vault / note.path

    if not note_path.exists():
        raise ValueError(f"Note file does not exist: '{note.path}'")

    with open(note_path, 'r', encoding='utf-8') as f:
        post = frontmatter.load(f)

    return post.content

def main():
    mcp.run("stdio", "expose_notes")

if __name__ == "__main__":
    main()
