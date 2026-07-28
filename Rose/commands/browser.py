"""
commands/browser.py
Functions that open things in the browser.
this file only knows *how*.
"""

import webbrowser
import platform

import webbrowser
import json

with open("config/search_sites.json") as f:
    _sites = json.load(f)


def search_site(site: str, query: str) -> str:
    """Searches `site` (looked up in config/search_sites.json) for `query`."""
    url_pattern = _sites.get(site.lower())

    if url_pattern is None:
        return f"I don't know how to search {site}"

    filtered_query = query.replace(" ", "+")
    webbrowser.open(url_pattern.format(query=filtered_query))
    return f"Searching {site} for {query}"