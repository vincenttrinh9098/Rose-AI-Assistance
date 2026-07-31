from plugins.base import Plugin
from commands.applications import control_app


class ControlAppPlugin(Plugin):
    name = "control_app"
    description = "null (use app_name and control_action instead)."
    extra_fields = {
        "app_name": {"type": ["string", "null"], "description": "The app to control. Only used for control_app."},
        "control_action": {"type": ["string", "null"], "description": "play, pause, next, previous, or quit. Only used for control_app."},
    }

    user_facing_description = "Say \"play/pause/skip on Spotify\" (or Apple Music) to control what's playing."
    def handle(self, query: str, app_name: str = None, control_action: str = None, **kwargs) -> str:
        return control_app(app_name, control_action)