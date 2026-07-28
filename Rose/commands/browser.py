"""
commands/browser.py
Functions that open things in the browser.
this file only knows *how*.
"""

import webbrowser
import platform

import webbrowser
import json


APPS_CONFIG_PATH = "config/search_sites.json"

try:
    with open(APPS_CONFIG_PATH) as f:
        _sites = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Warning: couldn't load {APPS_CONFIG_PATH}: {e}")
    _sites = {}



def search_site(site: str, query: str) -> str:
    """Searches `site` (looked up in config/search_sites.json) for `query`."""
    url_pattern = _sites.get(site.lower())

    if url_pattern is None:
        return f"I don't know how to search {site}"

    filtered_query = query.replace(" ", "+")
    webbrowser.open(url_pattern.format(query=filtered_query))
    return f"Searching {site} for {query}"