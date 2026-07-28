from plugins.base import Plugin
from commands.vscode import open_project


class OpenProjectPlugin(Plugin):
    name = "open_project"
    description = "Opens a project folder in VS Code, given a path or project name."
    extra_fields = {}

    def handle(self, query: str, **kwargs) -> str:
        return open_project(query)