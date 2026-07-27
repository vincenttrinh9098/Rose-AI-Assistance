"""
core/dispatcher.py

Takes transcribed text, asks Claude which action it maps to, calls the matching command.
"""

from commands.applications import open_app, control_app
from commands.browser import search_google,search_youtube
from commands.browser_reader import get_page_text
from commands.apple_calendar import add_calendar_event, list_todays_events
from commands.reminders import add_reminder
from commands.messages import send_message,find_contact_matches
from commands.notes import add_note

from ai.llm import get_action
from ai.text_analysis import analyze_text,general_question
from ai.event_parser import extract_event

from vision.locator import locate
from vision.clicker import click_at
from vision.screenshot import take_screenshot, take_screenshot_and_save
from vision.analyze import analyze_screen


from core.pending_action import get_pending, set_pending, clear_pending


from difflib import SequenceMatcher

def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def dispatch(text: str) -> str:
    pending = get_pending()
            
    if pending is not None:
        if "cancel" in text.lower() or "nevermind" in text.lower() or "never mind" in text.lower():
            clear_pending()
            return "Okay, cancelled."
        if pending["type"] == "disambiguate_contact":
            for name in pending["matches"]:
                if _similarity(text, name) > 0.7:
                    set_pending("confirm_send", recipient=name, content=pending["content"])
                    return f"Send '{pending['content']}' to {name}?"
            return "I didn't catch which one - could you repeat the name?"
        elif pending["type"] == "confirm_send":
            if "yes" in text.lower() or "yeah" in text.lower():
                answer = send_message(pending.get("recipient"), pending.get("content"))
                clear_pending()
                return answer
            elif "no" in text.lower():
                clear_pending()
                return "Okay, I won't send that"
            else:
                return "Should I send it? Yes or no?"
    result = get_action(text)
    action = result.get("action")
    query = result.get("query")
    app_name = result.get("app_name")
    control_action = result.get("control_action")
    recipient = result.get("recipient")
    content = result.get("content")
        
    #Commands
    if action == "open_app":
        confirm = open_app(query)
        return confirm
    
    elif action == "control_app":
        return control_app(app_name, control_action)

    elif "search_google" in action:
        search_google(query)
        return "Searching on google.." 
    
    elif "search_youtube" in action:
        search_youtube(query)
        return "Searching on youtube.." 
    
    elif action == "add_calendar_event":
        event = extract_event(query)
        return add_calendar_event(event["title"], event.get("date"), event.get("time"), event.get("duration_hours"))
    
    elif action == "list_todays_events":
        return list_todays_events() 
    
    elif action == "add_reminder":
        event = extract_event(query)
        return add_reminder(event["title"], event.get("date"), event.get("time"))

    elif action == "add_note":
        return add_note(query)
    
    elif action == "send_message":
            if not content or not recipient:
                return "Who should I send it to, and what should it say?"

            matches = find_contact_matches(recipient)
            if len(matches) == 0:
                return "I couldn't find that contact"
            elif len(matches) == 1:
                set_pending("confirm_send", recipient=matches[0], content=content)
                return f"Is {matches[0]} the correct person?"
            else:
                set_pending("disambiguate_contact", matches=matches, content=content)
                return f"I found a few matches: {', '.join(matches)}. Which one did you mean?"
                    
    #Vision
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

    #AI
    elif action == "general_question":
        answer = general_question(text)
        return answer
    
    else:
        return ("Sorry, I didn't quite get that...")