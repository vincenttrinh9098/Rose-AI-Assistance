from plugins.base import Plugin
from ai.text_analysis import general_question as _general_question


class GeneralQuestionPlugin(Plugin):
    name = "general_question"
    description = "any standalone question, opinion request, or piece of advice that is NOT about the current screen or webpage."
    extra_fields = {}

    def handle(self, query: str, **kwargs) -> str:
        return _general_question(query)