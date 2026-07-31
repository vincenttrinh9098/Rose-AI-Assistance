from plugins.base import Plugin
from commands.steam import launch_game


class LaunchGamePlugin(Plugin):
    name = "launch_game"
    description = "Launches a Steam game by name."
    extra_fields = {}

    def handle(self, query: str, **kwargs) -> str:
        return launch_game(query)