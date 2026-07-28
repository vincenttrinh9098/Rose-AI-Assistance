from plugins.base import Plugin
from commands.browser import search_google, search_youtube
from commands.applications import open_app


class OpenAppPlugin(Plugin):
    name = "open_app"
    description = "Opens an app or website by name."
    extra_fields = {}

    def handle(self, query: str, **kwargs) -> str:
        return open_app(query)


class SearchGooglePlugin(Plugin):
    name = "search_google"
    description = "Searches Google for the given terms."
    extra_fields = {}

    def handle(self, query: str, **kwargs) -> str:
        search_google(query)
        return "Searching on google.."


class SearchYoutubePlugin(Plugin):
    name = "search_youtube"
    description = "Searches YouTube for the given terms."
    extra_fields = {}

    def handle(self, query: str, **kwargs) -> str:
        search_youtube(query)
        return "Searching on youtube.."