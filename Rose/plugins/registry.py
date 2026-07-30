from plugins.notes_plugin import AddNotePlugin
from plugins.calendar_plugin import AddAppleCalendarEventPlugin, ListEventsPlugin,AddGoogleCalendarEventPlugin,ListGoogleEventsPlugin
from plugins.reminders_plugin import AddReminderPlugin
from plugins.browser_plugin import OpenAppPlugin, SearchSitePlugin 
from plugins.app_control_plugin import ControlAppPlugin
from plugins.messages_plugin import SendMessagePlugin
from plugins.vision_plugin import TakeScreenshotPlugin, ClickElementPlugin, AnalyzeScreenPlugin, AnalyzePagePlugin
from plugins.general_question_plugin import GeneralQuestionPlugin
from plugins.vscode_plugin import OpenProjectPlugin
from plugins.github_plugin import ListPRsPlugin, OpenRepoPlugin
from plugins.files_plugin import FindFilePlugin
from plugins.steam_plugin import LaunchGamePlugin
from plugins.calendar_plugin import AddGoogleCalendarEventPlugin, ListGoogleEventsPlugin, EditCalendarEventPlugin,DeleteCalendarEventPlugin



ALL_PLUGINS = [
    AddNotePlugin(),
    AddGoogleCalendarEventPlugin(),
    ListGoogleEventsPlugin(),
    EditCalendarEventPlugin(),
    DeleteCalendarEventPlugin(),
    AddReminderPlugin(),
    OpenAppPlugin(),
    SearchSitePlugin(),
    ControlAppPlugin(),
    SendMessagePlugin(),
    TakeScreenshotPlugin(),
    ClickElementPlugin(),
    AnalyzeScreenPlugin(),
    AnalyzePagePlugin(),
    GeneralQuestionPlugin(),
    OpenProjectPlugin(),
    OpenRepoPlugin(),
    LaunchGamePlugin(),
    ListPRsPlugin(),
    FindFilePlugin()
]

_by_name = {p.name: p for p in ALL_PLUGINS}


def get_plugin(action_name: str):
    return _by_name.get(action_name)


def get_all_action_names() -> list:
    return [p.name for p in ALL_PLUGINS]