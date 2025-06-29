
"""
Frontmatter Scanner

Tools to scan a directory for markdown files, extracts frontmatter data (Created, Description),
and generates a summary.json file with metadata for each file.
"""

import sys
import json
import re
from datetime import datetime
from pathlib import Path, PurePath
from typing import Dict, List, Optional
from pydantic import BaseModel

from expose_notes.configuration import DailyNotesConfig

class Note(BaseModel):
    note_id: int
    path: Optional[str]
    title: Optional[str]
    created: Optional[str]
    description: Optional[str]

class NoteSet(BaseModel):
    generated_by: str
    generated_on: str
    directory: str | None = None
    daily_notes: bool = False
    total_files: int
    notes: List[Note]

import frontmatter

LLM_SUMMARY_FILENAME = ".llm_summary.json"

def extract_title_from_path(path: Path) -> str:
    """Extract a readable title from filename."""
    filename = Path(path.name).stem
    return re.sub(r'\s*[-_]\s*', ' ', filename).title()

def parse_note(id, path: Path, post: frontmatter.Post) -> Note:
    """Parse frontmatter post to extract relevant fields."""
    title = post.get('title') or post.get('Title') or extract_title_from_path(path)
    created = post.get('Created') or post.get('created') or post.get('date') or post.get('Date')

    return Note(
        note_id=id,
        path=str(path) or None,
        title=str(title) or None,
        created=created.isoformat() if isinstance(created, datetime) else str(created) if created else None,
        description=str(post.get('Description') or post.get('description') or post.get('Summary') or post.get('summary')) if (post.get('Description') or post.get('description') or post.get('Summary') or post.get('summary')) is not None else None
    )

def scan_markdown_files(directory: Path) -> List[Note]:
    """Scan directory for markdown files and extract frontmatter data."""
    notes = []
    
    # Find all markdown files
    markdown_files = list(directory.glob("*.md")) + list(directory.glob("*.markdown"))
    
    for i, file_path in enumerate(sorted(markdown_files)):
        
        try:
            # Load frontmatter
            with open(file_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            
            # Build file metadata
            file_data = parse_note(
                id=i + 1,
                path=file_path,
                post=post
            )
            
            notes.append(file_data)
            
        except Exception as e:
            print(f"  Error processing {file_path.name}: {e}")
            continue
    
    return notes


def json_serializer(obj):
    """JSON serializer for objects not serializable by default json code"""
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def build_note_set_for_notes(notes: List[Note], output_path: Path) -> NoteSet:
    """Build the summary of notes."""
    return NoteSet(
        generated_by = "expose_notes",
        generated_on = datetime.now().isoformat(),
        directory = str(output_path.parent.resolve()),
        total_files = len(notes),
        notes = notes
    )

def build_note_set_for_source(directory: Path) -> NoteSet:
    """Build the summary of notes in the given directory."""
    notes = scan_markdown_files(directory)
    return build_note_set_for_notes(notes, directory / LLM_SUMMARY_FILENAME)

def save_summary_json(notes: List[Note], output_path: Path) -> None:
    """Save the summary of notes to a JSON file."""
    summary = build_note_set_for_notes(notes, output_path)

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False, default=json_serializer)
        print(f"Summary saved to: {output_path}")
    except Exception as e:
        print(f"Error saving summary.json: {e}")
        sys.exit(1)

def validate_directory(directory: PurePath) -> bool:
    """Validate if the given directory exists and is a directory."""
    path = Path(directory).resolve()
    if not path.exists():
        print(f"Error: Directory '{path}' does not exist")
        return False
    if not path.is_dir():
        print(f"Error: '{path}' is not a directory")
        return False
    return True

def parse(target_directory: str) -> None:
    """Parse markdown files for current directory."""

    directory = Path(target_directory).resolve()

    if not validate_directory(directory):
        sys.exit(1)

    results = scan_markdown_files(directory)
    
    # Save results
    output_path = directory / LLM_SUMMARY_FILENAME
    save_summary_json(results, output_path)

