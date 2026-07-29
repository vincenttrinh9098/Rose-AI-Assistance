from plugins.base import Plugin
from commands.messages import find_contact_matches
from core.pending_action import set_pending


class SendMessagePlugin(Plugin):
    name = "send_message"
    description = "null (use recipient and content instead)."
    extra_fields = {
        "recipient": {"type": ["string", "null"], "description": "Name of the person to message. Only used for send_message."},
        "content": {"type": ["string", "null"], "description": "The message text. Only used for send_message."},
    }
    
    def handle(self, query: str, recipient: str = None, content: str = None, **kwargs) -> str:
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
            numbered = [f"{i+1}. {name}" for i, name in enumerate(matches)]
            return f"I found a few matches: {'. '.join(numbered)}. Which one, or say the number?"