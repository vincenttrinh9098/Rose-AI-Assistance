"""
plugins/base.py

The shared contract every plugin must follow. dispatcher.py only ever
talks to plugins through this interface - it never needs to know what's
happening inside handle() (AppleScript, REST API, URL scheme, etc).
"""

from abc import ABC, abstractmethod


class Plugin(ABC):
    name: str            # the action name, e.g. "add_note" - must be unique across all plugins
    description: str     # tells Claude what this action is for, used to build the schema

    # fields this plugin needs from Claude, beyond the standard "query" field.
    # e.g. send_message needs {"recipient": {...}, "content": {...}}
    # leave as an empty dict if the plugin only needs "query"
    extra_fields: dict = {}

    @abstractmethod
    def handle(self, query: str, **kwargs) -> str:
        """
        Actually perform the action. `query` is always passed.
        `kwargs` contains whatever extra_fields declared (e.g. recipient=..., content=...).
        Returns a string to be spoken back to the user.
        """
        raise NotImplementedError