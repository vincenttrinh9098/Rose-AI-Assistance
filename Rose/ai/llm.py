"""
ai/llm.py

Sends transcribed text to Claude, gets back a structured action decision.
dispatch() will call this instead of doing string matching itself.
"""

import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()  # reads .env into environment variables

# TODO: create the Anthropic client once at import time
# Anthropic() automatically reads ANTHROPIC_API_KEY from the environment - no need to pass it manually
client = Anthropic()

SYSTEM_PROMPT = """You are a command router for a voice assistant.
Given the user's spoken text, respond with ONLY a raw JSON object and nothing else.
Do NOT wrap it in markdown code fences or backticks. Do NOT add any explanation.
Your entire response must be parseable directly by json.loads().

{"action": "open_app" | "search_google" | "none", "query": string or null}

- action must be one of: open_app, search_google, none
- for open_app, query is the name of the app or site to open (e.g. "spotify", "youtube")
- for search_google, query is the search terms
- query is null only when action is "none"
- if the text doesn't match any known action, use "none"
"""

def get_action(text: str) -> dict:
    """Sends text to Claude, returns a dict like {"action": ..., "query": ...}."""

    #1) Sends text to claude to return back dict
    response = client.messages.create(model='claude-haiku-4-5',max_tokens=100,system=SYSTEM_PROMPT,messages= [{"role": "user", "content": text}])

    #2) Strips leading json tag
    raw_text = response.content[0].text
    raw_text = raw_text.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")       # remove backticks from both ends
        raw_text = raw_text.replace("json", "", 1)  # remove the leading "json" language tag
        raw_text = raw_text.strip()

    #3) returns  the resulting dict
    return json.loads(raw_text)