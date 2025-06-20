from pathlib import Path
from typing import List

import frontmatter
from mcp.server.fastmcp import FastMCP
from expose_notes.configuration import NotesConfig, NoteSource, get_configuration
from expose_notes.frontmatter_reader import NoteSet, Note, build_summary


mcp = FastMCP("Expose Notes Scanner", "expose_notes")

config =  get_configuration()

if not config:
    config = NotesConfig(notes=[])

notes = config.notes

note_sets = [build_summary(Path(note.path)) for note in config.notes]

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
def get_note_set(source_id: int) -> NoteSet | None:
    """
    Get a specific note set by ID.

    param source_id: The ID of the note source.
    return: The NoteSetList object if found, otherwise None.
    """
    source = get_note_source(source_id)

    if not source:
        return None
    
    for note_set in note_sets:
        if note_set.directory == source.path:
            return note_set
    return None

def get_note(source_id: int, note_id: int) -> Note | None:
    """
    Get a specific note by source ID and note ID.

    param source_id: The ID of the note source.
    param note_id: The ID of the note set.
    return: The NoteSet object if found, otherwise None.
    """
    note_set = get_note_set(source_id)

    if not note_set:
        return None

    for note_set in note_set.notes:
        if note_set.note_id == note_id:
            return note_set
    return None

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
    
    note_path = Path(note.path)

    if not note_path.exists():
        raise ValueError(f"Note file does not exist: '{note.path}'")

    with open(note_path, 'r', encoding='utf-8') as f:
        post = frontmatter.load(f)

    return post.content

def main():
    mcp.run("stdio", "expose_notes")

if __name__ == "__main__":
    main()
