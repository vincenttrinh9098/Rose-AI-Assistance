from plugins.base import Plugin
from ai.text_analysis import general_question as _general_question


class GeneralQuestionPlugin(Plugin):
    name = "general_question"
    description = "any question, request for information, news, current events, "
    "or explanation where the user wants a SPOKEN ANSWER read back to them - including "
    "phrases like 'tell me about X', 'give me a report on X', 'what's happening with X'. "
    "This is the DEFAULT for informational requests. Only use search_google if the user "
    "explicitly asks to search/look something up in their browser."
    extra_fields = {}
    user_facing_description = "Ask me anything — questions, opinions, current events, or just chat."


    def handle(self, query: str, **kwargs) -> str:
        return _general_question(query)