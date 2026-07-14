"""
vision/locator.py
Takes a screenshot and a natural-language description of something on screen,
asks Claude to locate it, returns pixel coordinates.
"""

import base64
from ai.llm import client 

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

    # TODO: read the image file as bytes, then base64-encode it
    # step 1: open(image_path, "rb") opens the file in binary read mode - use it in a `with` block
    # step 2: .read() gets the raw bytes
    # step 3: base64.b64encode(...) encodes those bytes, but returns a bytes object -
    #         chain .decode("utf-8") on the end to turn it into a plain string
    with open(image_path, "rb") as f:
        raw_bytes = f.read()

    image_data = base64.b64encode(raw_bytes).decode("utf-8")

    # TODO: call client.messages.create(...) - same shape as get_action(), but:
    # - the "content" of the user message is now a LIST of two blocks instead of a plain string:
    #   [
    #     {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": image_data}},
    #     {"type": "text", "text": f"Find this element on the screen: {description}"}
    #   ]
    # - tools=LOCATE_TOOL, tool_choice forcing "report_location"
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=100,
        tools = LOCATE_TOOL,
        tool_choice={"type": "tool", "name": "report_location"},
        messages=[{"role": "user", "content":        [
         {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": image_data}},
         {"type": "text", "text": f"Find this element on the screen: {description}"}
      ]}])

    # TODO: same pattern as get_action() - loop response.content, find the tool_use block,
    # return its .input
    for block in response.content:
        if(block.type=="tool_use"):
            action = block.input

    return action