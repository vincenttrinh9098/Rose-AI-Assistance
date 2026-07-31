from plugins.base import Plugin
from commands.github_helper import list_open_prs, open_repo


class OpenRepoPlugin(Plugin):
    name = "open_repo"
    description = "Opens a specific GitHub repository page in the browser, given the repo's name."
    extra_fields = {}
    user_facing_description = "Say \"open the [repo name] repo\" to launch it on GitHub."

    def handle(self, query: str, **kwargs) -> str:
        return open_repo(query)
    
class ListPRsPlugin(Plugin):
    name = "list_prs"
    description = "..."
    extra_fields = {}
    user_facing_description = "Ask \"what are my open PRs on [repo]\" to hear your pull requests."

    def handle(self, query: str, **kwargs) -> str:
        return list_open_prs(query)