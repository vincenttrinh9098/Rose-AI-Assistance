"""
commands/files.py

Searches the filesystem using Spotlight (mdfind), ranks results by
filename relevance and recency, and opens the best match.
"""

import subprocess
import os



def search_files(query: str, limit: int = 5) -> list[str]:
    """Runs mdfind across several spacing/formatting variants of `query`,
    ranks results by filename match + recency (best first)."""

    variants = [
        query,
        query.replace(" ", ""),
        query.replace(" ", "-"),
        query.replace(" ", "_"),
    ]

    all_paths = set()
    for variant in variants:
        result = subprocess.run(["mdfind", "-name", variant], capture_output=True, text=True)
        paths = [p for p in result.stdout.strip().split("\n") if p]
        all_paths.update(paths)

    paths = list(all_paths)

    if not paths:
        return []

    scored = []
    for path in paths:
        filename_match = 1 if query.lower().replace(" ", "") in os.path.basename(path).lower().replace(" ", "").replace("-", "") else 0
        mtime = os.path.getmtime(path)
        scored.append((filename_match, mtime, path))

    scored.sort(reverse=True)

    ranked = [path for (_, _, path) in scored[:limit]]

    return ranked


def open_file(path: str) -> str:
    """Opens a file with its default application."""
    subprocess.run(["open", path])
    return f"Opening {os.path.basename(path)}"