from plugins.base import Plugin
from commands.github_helper import list_open_prs


class ListPRsPlugin(Plugin):
    name = "list_prs"
    description = "..."
    extra_fields = {}

    def handle(self, query: str, **kwargs) -> str:
        return list_open_prs(query)