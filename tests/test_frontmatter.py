from pathlib import Path
from datetime import datetime
from frontmatter import Post
from expose_notes.frontmatter_reader import parse_note, extract_title_from_path

def test_extract_title_from_filename():
    """
    Test the extract_title_from_filename function.
    """
    path = Path("example_file.md")
    assert extract_title_from_path(path) == "Example File"

def test_parse_note():
    """
    Test the parse_post function with a mock frontmatter post.
    """
    params = {
        "title": "Test Title",
        "Created": datetime(2023, 10, 1),
        "Description": "This is a test description."
    }

    post = Post(
        content="",
        **params
    )

    note = parse_note(1, Path("test/example_file.md"), post)
    
    assert note.note_id == 1
    assert note.path == "test/example_file.md"
    assert note.title == "Test Title"
    assert note.created == "2023-10-01T00:00:00"
    assert note.description == "This is a test description."