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
    description = "Searches a specific site (e.g. google, youtube, yelp) for the given terms, optionally in a specific city."
    extra_fields = {
        "site": {"type": ["string", "null"], "description": "The site to search on. Only used for search_site."},
        "city": {"type": ["string", "null"], "description": "The city to scope the search to (e.g. for Yelp). Defaults to Sacramento if not mentioned."},
    }

    def handle(self, query: str, site: str = None, city: str = None, **kwargs) -> str:
        if city:
            return search_site(site, query, city)
        return search_site(site, query)