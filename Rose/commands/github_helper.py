
"""
commands/github_helper.py
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

with open("config/github_repos.json") as f:
    _repos = json.load(f)

def list_open_prs(name: str) -> str:
    """Lists open PRs for a repo, looked up by name in config/github_repos.json."""


    repo = _repos.get(name.lower())

    if repo is None:
        return f"I don't know a repo called {name}"

    url = f"https://api.github.com/repos/{repo}/pulls"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        print("Status code:", response.status_code)
        print("Response body:", response.text)
        return f"Sorry, I couldn't check that repo"

    prs = response.json()
    if not prs:
        return "No open pull requests"

    titles = [pr["title"] for pr in prs]
    return f"You have {len(titles)} open pull requests: {', '.join(titles)}"