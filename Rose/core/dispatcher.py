"""
core/dispatcher.py

Takes transcribed text, asks Claude which action it maps to, calls the matching command.
"""

from commands.messages import send_message
from ai.llm import get_action
from core.pending_action import get_pending, set_pending, clear_pending
from plugins.registry import get_plugin
from difflib import SequenceMatcher
import re
import os

from commands.files import search_files,open_file

def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def dispatch(text: str) -> str:

    import random

    no_input_responses = [
        "Sorry, I didn't quite catch that.",
        "Could you say that again?",
        "I didn't hear anything. Could you try again?",
        "I'm sorry, I missed that.",
        "Would you mind repeating that?",
        "I didn't quite understand. Could you say it one more time?",
        "Could you repeat that for me?",
        "I think I missed what you said.",
        "I didn't catch that. What was that again?",
        "Sorry, could you try saying that again?",
        "I'm listening. Could you repeat that?",
        "Would you mind saying that one more time?",
        "I didn't quite hear you.",
        "Could you say that a little more clearly?",
        "I'm sorry, I didn't catch what you said.",
    ]

    if not text or not text.strip():
        return random.choice(no_input_responses)

    pending = get_pending()
            
    if pending is not None:
        if "cancel" in text.lower() or "nevermind" in text.lower() or "never mind" in text.lower():
            clear_pending()
            return "Okay, cancelled."
        if pending["type"] == "disambiguate_contact":
            match = re.search(r"\d+", text)
            if match:
                index = int(match.group()) - 1
                if 0 <= index < len(pending["matches"]):
                    name = pending["matches"][index]
                    set_pending("confirm_send", recipient=name, content=pending["content"])
                    return f"Send '{pending['content']}' to {name}?"

            for name in pending["matches"]:
                if _similarity(text, name) > 0.7:
                    set_pending("confirm_send", recipient=name, content=pending["content"])
                    return f"Send '{pending['content']}' to {name}?"

            return "I didn't catch which one - could you repeat the name or say the number?"
        
        elif pending["type"] == "disambiguate_file":
            # Path 1: check for a spoken number first
            match = re.search(r"\d+", text)
            if match:
                index = int(match.group()) - 1
                if 0 <= index < len(pending["matches"]):
                    selected_path = pending["matches"][index]
                    clear_pending()
                    return open_file(selected_path)

            # Path 2: no valid number - try fuzzy matching against filenames
            for path in pending["matches"]:
                filename = os.path.basename(path)
                if _similarity(text, filename) > 0.5:
                    clear_pending()
                    return open_file(path)

            # Path 3: neither worked - check if this is actually a new command
            check = get_action(text)
            if check.get("action") not in (None, "none"):
                clear_pending()
                action = check.get("action")
                query = check.get("query")
                plugin = get_plugin(action)
                if plugin is not None:
                    extra_kwargs = {field: check.get(field) for field in plugin.extra_fields}
                    return plugin.handle(query, **extra_kwargs)

            return "Which number did you mean?"

        elif pending["type"] == "disambiguate_calendar_edit":
            match = re.search(r"\d+", text)
            if match:
                index = int(match.group()) - 1
                if 0 <= index < len(pending["matches"]):
                    from plugins.calendar_plugin import EditCalendarEventPlugin
                    selected_event = pending["matches"][index]
                    clear_pending()
                    return EditCalendarEventPlugin()._apply_edit(selected_event, pending["edit_info"])
            return "Which number did you mean?"


        elif pending["type"] == "disambiguate_calendar_delete":
            match = re.search(r"\d+", text)
            if match:
                index = int(match.group()) - 1
                if 0 <= index < len(pending["matches"]):
                    from commands.google_calendar import delete_google_calendar_event
                    selected_event = pending["matches"][index]
                    clear_pending()
                    return delete_google_calendar_event(selected_event["id"])
            return "Which number did you mean?"

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

    if action == "offline":
        return "I'm having trouble connecting right now — check your internet connection and if you are missing the Anthropic API key"
    elif action == "credits_error":
        return "I'm out of API credits — you'll need to add more at console.anthropic.com"

    plugin = get_plugin(action)
    if plugin is not None:
        extra_kwargs = {field: result.get(field) for field in plugin.extra_fields}
        query = query or ""
        response = plugin.handle(query, **extra_kwargs)
        from core.last_action import set_last_action
        set_last_action(action, query, response)

        return response


    return random.choice(no_input_responses)

