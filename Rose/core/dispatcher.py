"""
core/dispatcher.py

Takes transcribed text, asks Claude which action it maps to, calls the matching command.
"""

from commands.browser import open_youtube, open_google, search_google
from ai.llm import get_action


def dispatch(text: str) -> str:
    """
    Given transcribed text, run the matching command.
    Returns a string to be spoken back to the user (confirmation or error).
    """

    # Step 1: call get_action(text) to get back a dict like {"action": ..., "query": ...}
    result = get_action(text)

    # Step 2: pull the "action" and "query" values out of that dict
    action = result["action"]
    query = result["query"]

    # Step 3: match on `action` (not raw text anymore) and call the right function
    # - "open_youtube" -> open_youtube(), return confirmation
    # - "open_google" -> open_google(), return confirmation
    # - "search_google" -> search_google(query), return confirmation (use `query` this time, not extracted text)
    # - "none" or anything unrecognized -> return the "didn't understand" message

    action = action.lower()

    if "open_youtube" in action:
        open_youtube()
        return "Opening up youtube right now for you"
    elif "open_google" in action:
        open_google()
        return "Opening up google right now for you"
    elif "search_google" in action:
        search_google(query)
        return "Searching on google.." 
    else:
        return ("Sorry, I didn't quite get that...")