"""
commands/files.py

Searches the filesystem using Spotlight (mdfind), ranks results by
filename relevance and recency, and opens the best match.
"""

import subprocess
import os



def search_files(query: str, limit: int = 5) -> list[str]:
    """Runs mdfind, returns up to `limit` matching file paths, ranked by
    filename match + recency (best first)."""

    result = subprocess.run(["mdfind", "-name", query], capture_output=True, text=True)
    paths = [p for p in result.stdout.strip().split("\n") if p]

    if not paths:
        return []

    scored = []
    for path in paths:
        filename_match = 1 if query.lower() in os.path.basename(path).lower() else 0
        mtime = os.path.getmtime(path)
        scored.append((filename_match, mtime, path))

    scored.sort(reverse=True)

    ranked = [path for (_, _, path) in scored[:limit]]

    return ranked



def open_file(path: str) -> str:
    """Opens a file with its default application."""
    subprocess.run(["open", path])
    return f"Opening {os.path.basename(path)}"