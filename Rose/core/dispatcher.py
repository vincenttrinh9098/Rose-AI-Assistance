"""
core/dispatcher.py

Takes transcribed text, asks Claude which action it maps to, calls the matching command.
"""

from commands.applications import open_app, control_app
from commands.browser import search_google,search_youtube
from commands.browser_reader import get_page_text
from commands.apple_calendar import add_event

from ai.llm import get_action
from ai.text_analysis import analyze_text,general_question
from ai.event_parser import extract_event

from vision.locator import locate
from vision.clicker import click_at
from vision.screenshot import take_screenshot, take_screenshot_and_save
from vision.analyze import analyze_screen


def dispatch(text: str) -> str:

    result = get_action(text)
    action = result["action"]
    query = result["query"]
    app_name = result["app_name"]
    control_action = result["control_action"]

    if action == "open_app":
        confirm = open_app(query)
        return confirm
    if action == "control_app":
        return control_app(app_name, control_action)
    
    elif action == "take_screenshot":
        path = take_screenshot_and_save()
        print("Screenshot path is: ", path)
        return "Took a screenshot"
    
    elif action == "click_element":
        path = take_screenshot()
        result = locate(path,query)
        if(result["found"]==False):
            return "Couldn't find that"
        click_at(result["x"], result["y"], path)
        return "Clicking!"
    
    elif action == "analyze_screen":
       path = take_screenshot()
       answer = analyze_screen(path, query)
       return answer
    
    elif action == "analyze_page":
        text = get_page_text()
        answer = analyze_text(text, query)
        return answer
    
    elif action == "general_question":
        answer = general_question(text)
        return answer
    
    elif action == "add_calendar_event":
        event = extract_event(query)
        return add_event(event["title"], event["date"], event["time"], event["duration_hours"])

    elif "search_google" in action:
        search_google(query)
        return "Searching on google.." 
    
    elif "search_youtube" in action:
        search_youtube(query)
        return "Searching on youtube.." 
    
    else:
        return ("Sorry, I didn't quite get that...")