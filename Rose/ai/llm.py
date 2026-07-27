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
                    "enum": ["open_app", "search_google","search_youtube", "click_element", "take_screenshot","analyze_screen","analyze_page", "none"],
                },
                "query": {
                    "type": ["string", "null"],
                    "description": "App name for open_app, search terms for search_google/search_youtube, element description for click_element, question to ask for analyze_screen, question to ask for anaylze_page null for take_screenshot/none",
                },
            },
            "required": ["action", "query"],
        },
    }
]


def get_action(text: str) -> dict:
    # TODO: call client.messages.create(...) same as before, but:
    # - add tools=TOOLS
    # - add tool_choice={"type": "tool", "name": "route_command"} to FORCE it to use this tool
    #   (without this, Claude might choose not to use the tool at all)
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=100,
        tools=TOOLS,
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