"""
vision/locator.py
Takes a screenshot and a natural-language description of something on screen,
asks Claude to locate it, returns pixel coordinates.
"""

import base64
from ai.client import client

LOCATE_TOOL = [
    {
        "name": "report_location",
        "description": "Reports the pixel coordinates of an element found in a screenshot.",
        "input_schema": {
            "type": "object",
            "properties": {
                "found": {
                    "type": "boolean",
                    "description": "Whether the described element was found in the image",
                },
                "x": {"type": "integer", "description": "x coordinate of the element's center"},
                "y": {"type": "integer", "description": "y coordinate of the element's center"},
            },
            "required": ["found", "x", "y"],
        },
    }
]


def locate(image_path: str, description: str) -> dict:
    """Given a screenshot path and a description, returns {"found": bool, "x": int, "y": int}."""
    if not description or not description.strip():
        description = "the main visible element on screen"

    with open(image_path, "rb") as f:
        raw_bytes = f.read()

    image_data = base64.b64encode(raw_bytes).decode("utf-8")


    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=100,
        tools = LOCATE_TOOL,
        tool_choice={"type": "tool", "name": "report_location"},
        messages=[{"role": "user", "content":        [
         {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": image_data}},
         {"type": "text", "text": f"Find this element on the screen: {description}"}
      ]}])


    for block in response.content:
        if(block.type=="tool_use"):
            action = block.input

    return action