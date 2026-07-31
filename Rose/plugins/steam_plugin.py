from plugins.base import Plugin
from commands.steam import launch_game


class LaunchGamePlugin(Plugin):
    name = "launch_game"
    description = "Launches a Steam game by name."
    extra_fields = {}
    user_facing_description = "Say \"launch my game \[name]\ on Steam\""
    def handle(self, query: str, **kwargs) -> str:
        return launch_game(query)