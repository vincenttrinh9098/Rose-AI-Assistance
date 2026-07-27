"""
commands/browser_reader.py

Reads the active browser tab's URL and page content, for features like
"analyze this article" that need the full page, not just what's visible
on screen.
"""

import subprocess
import requests
from bs4 import BeautifulSoup



def get_active_chrome_url() -> str:
    """Returns the URL of the currently active tab in Chrome."""
    script = '''
    tell application "Google Chrome"
        get URL of active tab of front window
    end tell
    '''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    return result.stdout.strip()


def get_rendered_html() -> str:
    """Gets the ALREADY-RENDERED HTML of the active Chrome tab, via JavaScript."""
    script = '''
    tell application "Google Chrome"
        execute active tab of front window javascript "document.documentElement.outerHTML"
    end tell
    '''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    return result.stdout


def get_page_text() -> str:
    """Extracts readable text from the currently active Chrome tab's rendered content."""
    html = get_rendered_html()
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "nav", "header", "footer"]): 
        tag.decompose()


    text = soup.get_text(separator=" ", strip=True) 

    return text