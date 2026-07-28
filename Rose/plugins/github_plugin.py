from plugins.base import Plugin
from commands.github_helper import list_open_prs, open_repo


class OpenRepoPlugin(Plugin):
    name = "open_repo"
    description = "Opens a specific GitHub repository page in the browser, given the repo's name."
    extra_fields = {}

    def handle(self, query: str, **kwargs) -> str:
        return open_repo(query)
    
class ListPRsPlugin(Plugin):
    name = "list_prs"
    description = "..."
    extra_fields = {}

    def handle(self, query: str, **kwargs) -> str:
        return list_open_prs(query)