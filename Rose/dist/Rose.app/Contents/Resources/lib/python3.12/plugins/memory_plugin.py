from plugins.base import Plugin
from core.long_term_memory import remember_fact
from ai.memory_parser import extract_memory


class RememberFactPlugin(Plugin):
    name = "remember_fact"
    description = (
        "Stores a fact the user EXPLICITLY asks to be remembered long-term. "
        "REQUIRED: the phrase must contain an explicit memory-trigger word or phrase like "
        "'remember', 'don't forget', or 'keep in mind'. "
        "If the phrase does NOT contain one of these trigger words, even if it sounds like "
        "a fact about the user (e.g. 'my favorite color is blue', 'I live in Sacramento'), "
        "do NOT use this action - use general_question instead. "
        "The presence of the trigger word is mandatory, not optional."
    )
    extra_fields = {}

    def handle(self, query: str, **kwargs) -> str:
        memory_info = extract_memory(query)
        remember_fact(memory_info["category"], memory_info["key"], memory_info["value"])
        return f"Got it, I'll remember {memory_info['value']}"