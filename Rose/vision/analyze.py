"""
vision/analyze.py

Takes a screenshot and a question, asks Claude to describe/analyze what's
in the image, returns Claude's natural-language answer as plain text.
"""

import base64
from ai.client import client


def analyze_screen(image_path: str, question: str) -> str:
    """Sends a screenshot + question to Claude, returns Claude's text answer."""
    if not question or not question.strip():
        question = "What is on this screen?"

    with open(image_path, "rb") as f:
        raw_bytes = f.read()

    image_data = base64.b64encode(raw_bytes).decode("utf-8")
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=500,
        messages=[{"role": "user", "content":        [
         {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": image_data}},
         {"type": "text", "text": f"{question}\n\nAnswer in 1-3 natural spoken sentences, as if you're describing this out loud to someone who can't see the screen. Do not use any markdown formatting, bullet points, headers, or symbols like # or * or -. Just plain conversational sentences."}
      ]}])

    return response.content[0].text