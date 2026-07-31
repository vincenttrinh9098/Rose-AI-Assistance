"""
commands/browser.py
Functions that open things in the browser.
this file only knows *how*.
"""

import webbrowser
import platform

import webbrowser
import json


from core.paths import path_for
SEARCH_SITES_PATH = path_for("config", "search_sites.json")

try:
    with open(SEARCH_SITES_PATH) as f:
        _sites = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Warning: couldn't load {SEARCH_SITES_PATH}: {e}")
    _sites = {}



def search_site(site: str, query: str, city: str = "Sacramento, CA") -> str:
    """Searches `site` (looked up in config/search_sites.json) for `query`, optionally scoped to `city`."""
    url_pattern = _sites.get(site.lower())

    if url_pattern is None:
        return f"I don't know how to search {site}"

    filtered_query = query.replace(" ", "+")
    filtered_city = city.replace(" ", "+").replace(",", "%2C")

    url = url_pattern.format(query=filtered_query, city=filtered_city) if "{city}" in url_pattern else url_pattern.format(query=filtered_query)

    webbrowser.open(url)
    return f"Searching {site} for {query}"