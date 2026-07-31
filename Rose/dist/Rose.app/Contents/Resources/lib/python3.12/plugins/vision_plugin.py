from plugins.base import Plugin
from vision.screenshot import take_screenshot, take_screenshot_and_save
from vision.locator import locate
from vision.clicker import click_at
from vision.analyze import analyze_screen
from commands.browser_reader import get_page_text
from ai.text_analysis import analyze_text


class TakeScreenshotPlugin(Plugin):
    name = "take_screenshot"
    description = "null."
    extra_fields = {}

    def handle(self, query: str, **kwargs) -> str:
        path = take_screenshot_and_save()
        print("Screenshot path is: ", path)
        return "Took a screenshot"


class ClickElementPlugin(Plugin):
    name = "click_element"
    description = "a description of the on-screen element to click."
    extra_fields = {}

    def handle(self, query: str, **kwargs) -> str:
        path = take_screenshot()
        result = locate(path, query)
        if result["found"] == False:
            return "Couldn't find that"
        click_at(result["x"], result["y"], path)
        return "Clicking!"


class AnalyzeScreenPlugin(Plugin):
    name = "analyze_screen"
    description = "the question about what's visually on screen right now."
    extra_fields = {}

    def handle(self, query: str, **kwargs) -> str:
        path = take_screenshot()
        return analyze_screen(path, query)


class AnalyzePagePlugin(Plugin):
    name = "analyze_page"
    description = "the question about the CURRENT webpage/article's content or text."
    extra_fields = {}

    def handle(self, query: str, **kwargs) -> str:
        text = get_page_text()
        return analyze_text(text, query)