"""
plugins/base.py

The shared contract every plugin must follow. dispatcher.py only ever
talks to plugins through this interface - it never needs to know what's
happening inside handle() (AppleScript, REST API, URL scheme, etc).
"""

from abc import ABC, abstractmethod


class Plugin(ABC):
    name: str
    description: str
    extra_fields: dict = {}
    user_facing_description: str = ""  # optional, human-friendly explanation for the Capabilities tab

    @abstractmethod
    def handle(self, query: str, **kwargs) -> str:
        ...