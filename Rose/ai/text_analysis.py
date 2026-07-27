"""
analyze_text() - "understand this text" functions
"""

import os
from dotenv import load_dotenv
from anthropic import Anthropic
from ai.llm import client

def analyze_text(text: str, question: str) -> str:
    """Sends page text + a question to Claude, returns Claude's spoken-style answer."""

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=500,
        messages=[{"role": "user", "content": f"Here is the content of a webpage:\n\n{text}\n\nQuestion: {question}\n\nAnswer in 1-3 natural spoken sentences, no markdown formatting."}],    
)
    return response.content[0].text