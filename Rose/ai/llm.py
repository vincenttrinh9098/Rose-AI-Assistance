"""
ai/llm.py - now using tool use / structured output instead of prompted JSON.
"""


from ai.client import client

from plugins.registry import get_all_action_names, ALL_PLUGINS

def build_tools_schema():
    action_names = get_all_action_names() + ["none"]
    query_description_parts = [f"{p.name}: {p.description}" for p in ALL_PLUGINS]

    properties = {
        "action": {"type": "string", "enum": action_names},
        "query": {"type": ["string", "null"], "description": " ".join(query_description_parts)},
    }
    for p in ALL_PLUGINS:
        properties.update(p.extra_fields)

    return [{
        "name": "route_command",
        "description": "Routes a voice command to the correct action.",
        "input_schema": {"type": "object", "properties": properties, "required": list(properties.keys())},
    }]

TOOLS = build_tools_schema()


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

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=100,
        tools=TOOLS,
        system=DISAMBIGUATION_RULES,
        tool_choice={"type": "tool", "name": "route_command"},
        messages=[{"role": "user", "content": text}],

    )  
    for block in response.content:
        if(block.type=="tool_use"):
            action_data = block.input

    return action_data