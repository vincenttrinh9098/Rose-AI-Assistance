from plugins.base import Plugin
from core.long_term_memory import remember_fact
from ai.memory_parser import extract_memory


class RememberFactPlugin(Plugin):
    name = "remember_fact"
    description = (
        "Stores a fact the user explicitly asks to be remembered long-term "
        "(e.g. 'remember that I go to this specific school', 'remember I like dark mode', "
        "'remember my project is called Rose'). Only use this when the user "
        "clearly wants something permanently remembered, not for casual mentions."
    )
    extra_fields = {}

    def handle(self, query: str, **kwargs) -> str:
        memory_info = extract_memory(query)
        remember_fact(memory_info["category"], memory_info["key"], memory_info["value"])
        return f"Got it, I'll remember {memory_info['value']}"