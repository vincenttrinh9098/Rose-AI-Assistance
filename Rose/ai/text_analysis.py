"""
analyze_text() - "understand this text" functions
"""

import os
from ai.client import client
from core.conversation import get_history, add_exchange

ROSE_IDENTITY = """You are Rose, a personal voice assistant running on the user's Mac. Unlike a typical AI chatbot, you have real capabilities through connected tools: you can open apps and websites, search and open files, add/edit/delete calendar events, send messages, set reminders, take notes, control media playback (Spotify, Apple Music), analyze what's on the user's screen, browse and summarize webpages, remember facts about the user long-term, and answer general questions with web search.
When asked what you can do, describe these real capabilities confidently and specifically - never say things like "I can't open apps" or "I'm just a language model" or "I don't have the ability to interact with your device." You genuinely do, through the assistant system you're part of. Speak as Rose, not as a generic AI assistant describing its limitations."""


def analyze_text(text: str, question: str) -> str:
    """Sends page text + a question to Claude, returns Claude's spoken-style answer."""
    if not question or not question.strip():
        question = "What is this about?"
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=500,
        messages=[{"role": "user", "content": f"Here is the content of a webpage:\n\n{text}\n\nQuestion: {question}\n\nAnswer in 1-3 natural spoken sentences, no markdown formatting."}],    
)
    return response.content[0].text

def guess_url(site_name: str) -> str | None:
    if not site_name or not site_name.strip():
        return None
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=50,
        messages=[{"role": "user", "content": (
            f"A user said 'open {site_name}' to their voice assistant, wanting to open "
            f"a website or app in their browser. This is very likely a well-known company, "
            f"app, or service name (possibly slightly mis-transcribed by speech recognition). "
            f"What is the most likely website URL they meant? "
            f"Respond with ONLY the URL. If genuinely no reasonable guess exists, respond 'UNKNOWN'."
        )}],
    )
    text = response.content[0].text.strip()
    if text == "UNKNOWN" or not text.startswith("http"):
        return None
    return text

ROSE_IDENTITY = """You are Rose, a personal voice assistant running on the user's Mac. Unlike a typical AI chatbot, you have real capabilities through connected tools: you can open apps and websites, search and open files, add/edit/delete calendar events, send messages, set reminders, take notes, control media playback (Spotify, Apple Music), analyze what's on the user's screen, browse and summarize webpages, remember facts about the user long-term, and answer general questions with web search.

When asked what you can do, describe these real capabilities confidently and specifically - never say things like "I can't open apps" or "I'm just a language model" or "I don't have the ability to interact with your device." You genuinely do, through the assistant system you're part of. Speak as Rose, not as a generic AI assistant describing its limitations."""


def general_question(question: str) -> str:
    """Sends a general question to Claude, with web search enabled, returns a spoken-style answer."""
    from core.long_term_memory import format_memory_for_prompt

    if not question or not question.strip():
        question = "hello"

    history = get_history()
    memory_context = format_memory_for_prompt()

    system_prompt = ROSE_IDENTITY
    if memory_context:
        system_prompt += f"\n\n{memory_context}"

    kwargs = {
        "model": "claude-haiku-4-5",
        "max_tokens": 500,
        "system": system_prompt,
        "tools": [{"type": "web_search_20250305", "name": "web_search"}],
        "messages": history + [{"role": "user", "content": f"{question}\n\nAnswer in 2-4 natural spoken sentences, as if speaking out loud. No markdown formatting."}],
    }

    response = client.messages.create(**kwargs)

    text_blocks = []
    for block in response.content:
        if block.type == "text":
            text_blocks.append(block.text)
    answer = " ".join(text_blocks)

    add_exchange(question, answer)

    return answer