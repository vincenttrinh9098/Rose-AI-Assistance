"""
plugins/notes_plugin.py
"""

from plugins.base import Plugin
from commands.notes import add_note as _add_note


class AddNotePlugin(Plugin):
    name = "add_note"
    description = "Creates a note with the given content."
    extra_fields = {}

    def handle(self, query: str, **kwargs) -> str:
        return _add_note(query)