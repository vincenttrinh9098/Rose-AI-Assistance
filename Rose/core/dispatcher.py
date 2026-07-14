"""
core/dispatcher.py

Takes transcribed text, asks Claude which action it maps to, calls the matching command.
"""

from commands.applications import open_app
from commands.browser import search_google
from ai.llm import get_action

from vision.locator import locate
from vision.clicker import click_at
from vision.screenshot import take_screenshot, take_screenshot_and_save

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
    elif action == "take_screenshot":
        path = take_screenshot_and_save()
        print("Screenshot path is: ", path)
        return "Took a screenshot"
    elif action == "click_element":
        path = take_screenshot()

        result = locate(path,query)

        # Step 3: check result["found"] - if False, return a "couldn't find that" message
        if(result["found"]==False):
            return "Couldn't find that"
        click_at(result["x"], result["y"], path)

        return "Clicking!"

    elif "search_google" in action:
        search_google(query)
        return "Searching on google.." 
    else:
        return ("Sorry, I didn't quite get that...")