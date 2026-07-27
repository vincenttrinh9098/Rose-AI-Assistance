"""
analyze_text() - "understand this text" functions
"""

import os
from ai.llm import client

def analyze_text(text: str, question: str) -> str:
    """Sends page text + a question to Claude, returns Claude's spoken-style answer."""

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=500,
        messages=[{"role": "user", "content": f"Here is the content of a webpage:\n\n{text}\n\nQuestion: {question}\n\nAnswer in 1-3 natural spoken sentences, no markdown formatting."}],    
)
    return response.content[0].text

def general_question(question: str) -> str:
    """Sends a general question to Claude, with web search enabled, returns a spoken-style answer."""

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=500,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": f"{question}\n\nAnswer in 2-4 natural spoken sentences, as if speaking out loud. No markdown formatting."}],
    )


    text_blocks = []
    for block in response.content:
        if block.type == "text":
            text_blocks.append(block.text)
    answer = " ".join(text_blocks)

    return answer