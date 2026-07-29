from plugins.base import Plugin
from commands.applications import open_app
from commands.browser import search_site


class OpenAppPlugin(Plugin):
    name = "open_app"
    description = "Opens an app or website by name."
    extra_fields = {}

    def handle(self, query: str, **kwargs) -> str:
        return open_app(query)


class SearchSitePlugin(Plugin):
    name = "search_site"
    
    description = (
        "ONLY use this when the user explicitly wants to open search results in their "
        "browser (e.g. 'search google for X', 'look up X on youtube'). "
        "Do NOT use this for questions, news requests, or anything where the user wants "
        "a spoken answer - use general_question instead for those."
    )

    extra_fields = {
        "site": {"type": ["string", "null"], "description": "The site to search on. Only used for search_site."},
    }

    def handle(self, query: str, site: str = None, **kwargs) -> str:
        return search_site(site, query)