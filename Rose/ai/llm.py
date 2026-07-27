"""
ai/llm.py - now using tool use / structured output instead of prompted JSON.
"""

import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

# TODO: define the tool schema. This describes a function called "route_command"
# with two parameters:
# - "action": a string that must be one of a fixed set (use "enum" in JSON schema)
# - "query": a string, allowed to be null/omitted
TOOLS = [
    {
        "name": "route_command",
        "description": "Routes a voice command to the correct action.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "open_app",
                        "search_google",
                        "search_youtube",
                        "click_element",
                        "take_screenshot",
                        "analyze_screen",
                        "analyze_page",
                        "general_question",
                        "none",
                    ],
                },
                "query": {
                    "type": ["string", "null"],
                    "description": (
                        "open_app: the app or site name. "
                        "search_google / search_youtube: the search terms. "
                        "click_element: a description of the on-screen element to click. "
                        "analyze_screen: the question about what's visually on screen right now. "
                        "analyze_page: the question about the CURRENT webpage/article's content or text. "
                        "general_question: any standalone question, opinion request, or "
                        "piece of advice that is NOT about the current screen or webpage. "
                        "take_screenshot / none: null."
                    ),
                },
            },
            "required": ["action", "query"],
        },
        "cache_control": None,
    }
]

DISAMBIGUATION_RULES = """
When choosing between analyze_screen, analyze_page, and general_question:
- Use analyze_page ONLY if the user references "this page", "this article", "this site",
  or clearly implies they want the content of the currently open webpage summarized/explained.
- Use analyze_screen if the user references "this screen", "what I'm looking at", or something
  visual that isn't specifically article/text content (e.g. "what does this image show").
- Use general_question for anything else: opinions, advice, standalone factual questions,
  current events, or questions with no reference to the current screen/page at all.
- When in doubt between analyze_page and general_question, prefer general_question unless
  the user explicitly signals they're asking about "this" specific page/article.
"""

def get_action(text: str) -> dict:
    # TODO: call client.messages.create(...) same as before, but:
    # - add tools=TOOLS
    # - add tool_choice={"type": "tool", "name": "route_command"} to FORCE it to use this tool
    #   (without this, Claude might choose not to use the tool at all)
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=100,
        tools=TOOLS,
        system=DISAMBIGUATION_RULES,
        tool_choice={"type": "tool", "name": "route_command"},
        messages=[{"role": "user", "content": text}],
    
)
    # TODO: find the tool_use block in response.content
    # unlike before, response.content might have multiple blocks - loop through and
    # find the one where block.type == "tool_use"
    # that block's .input is ALREADY a dict - no json.loads() needed at all
  
    for block in response.content:
        if(block.type=="tool_use"):
            action_data = block.input

    return action_data