from plugins.base import Plugin
from commands.messages import find_contact_matches
from core.pending_action import set_pending


def _is_placeholder(value: str) -> bool:
    return not value or "UNKNOWN" in value.upper() or value.upper() in ("NONE", "NULL", "")


class SendMessagePlugin(Plugin):
    name = "send_message"
    description = "null (use recipient and content instead)."
    extra_fields = {
        "recipient": {"type": ["string", "null"], "description": "Name of the person to message. Only used for send_message."},
        "content": {"type": ["string", "null"], "description": "The message text. Only used for send_message."},
    }
    user_facing_description = "Say \"send a message to [name] saying [something]\" and I'll find them in your contacts and send it, confirming before it goes out."

    def handle(self, query: str, recipient: str = None, content: str = None, **kwargs) -> str:
        if _is_placeholder(content) or _is_placeholder(recipient):
            return "Who should I send it to, and what should it say?"

        matches = find_contact_matches(recipient)
        if len(matches) == 0:
            return "I couldn't find that contact"
        elif len(matches) == 1:
            set_pending("confirm_send", recipient=matches[0], content=content)
            return f"Send '{content}' to {matches[0]}, is that correct?"
        else:
            set_pending("disambiguate_contact", matches=matches, content=content)
            numbered = [f"{i+1}. {name}" for i, name in enumerate(matches)]
            return f"I found a few matches: {'. '.join(numbered)}. Which one, or say the number?"