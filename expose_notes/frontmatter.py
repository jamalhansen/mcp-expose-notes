
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

import frontmatter

LLM_SUMMARY_FILENAME = ".llm_summary.json"

def extract_title_from_path(path: Path) -> str:
    """Extract a readable title from filename."""
    filename = Path(path.name).stem
    return re.sub(r'\s*[-_]\s*', ' ', filename).title()

def parse_post(id, relative_path: Path, post: frontmatter.Post) -> Dict[str, Optional[str]]:
    """Parse frontmatter post to extract relevant fields."""
    title = post.get('title') or post.get('Title') or extract_title_from_path(relative_path)
    created = post.get('Created') or post.get('created') or post.get('date') or post.get('Date')

    return {
        "id": id,
        "relative_path": str(relative_path) or None,
        "title": str(title) or None,
        "created": created.isoformat() if isinstance(created, datetime) else str(created) if created else None,
        "description": str(post.get('Description') or post.get('description') or post.get('Summary') or post.get('summary')) if (post.get('Description') or post.get('description') or post.get('Summary') or post.get('summary')) is not None else None
    }

def scan_markdown_files(directory: Path) -> List[Dict]:
    """Scan directory for markdown files and extract frontmatter data."""
    results = []
    
    # Find all markdown files
    markdown_files = list(directory.glob("*.md")) + list(directory.glob("*.markdown"))
    
    for i, file_path in enumerate(sorted(markdown_files)):
        
        try:
            # Load frontmatter
            with open(file_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            
            # Extract relative path from the scan directory
            relative_path = file_path.relative_to(directory)
            
            # Build file metadata
            file_data = parse_post(
                id=i + 1,
                relative_path=relative_path,
                post=post
            )
            
            results.append(file_data)
            
        except Exception as e:
            print(f"  Error processing {file_path.name}: {e}")
            continue
    
    return results


def json_serializer(obj):
    """JSON serializer for objects not serializable by default json code"""
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def save_summary_json(data: List[Dict], output_path: Path) -> None:
    """Save the extracted data to summary.json."""
    summary = {
        "generated_by": "frontmatter_scanner.py",
        "generated_on": datetime.now().isoformat(),
        "directory": str(output_path.parent.resolve()),
        "total_files": len(data),
        "files": data
    }
    
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

