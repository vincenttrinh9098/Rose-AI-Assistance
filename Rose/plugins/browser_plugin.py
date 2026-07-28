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
    description = "Searches a specific site (e.g. google, youtube, walmart, amazon) for the given terms."
    extra_fields = {
        "site": {"type": ["string", "null"], "description": "The site to search on. Only used for search_site."},
    }

    def handle(self, query: str, site: str = None, **kwargs) -> str:
        return search_site(site, query)