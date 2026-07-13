"""
core/dispatcher.py

Takes transcribed text, asks Claude which action it maps to, calls the matching command.
"""

from commands.applications import open_app
from commands.browser import search_google
from ai.llm import get_action

def dispatch(text: str) -> str:
    result = get_action(text)
    action = result["action"]
    query = result["query"]

    # Step 1: if action == "open_app", call open_app(query) and return its result directly
    # (open_app already returns the confirmation string - no need to write your own here)

    # Step 2: if action == "search_google", call search_google(query), return a confirmation

    # Step 3: else, return the "didn't understand" message

    if action == "open_app":
        confirm = open_app(query)
        return confirm
    elif "search_google" in action:
        search_google(query)
        return "Searching on google.." 
    else:
        return ("Sorry, I didn't quite get that...")