"""
core/conversation_log.py

Writes structured conversation history (separate from the raw debug log)
for the GUI's conversation-view tab to read.
"""

import json
from datetime import datetime

from core.paths import path_for
LOG_PATH = path_for("logs", "conversation.jsonl")


def log_exchange(user_text: str, assistant_text: str) -> None:
    """Appends one user/assistant exchange as two JSON lines."""
    timestamp = datetime.now().isoformat()
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps({"role": "user", "text": user_text, "timestamp": timestamp}) + "\n")
        f.write(json.dumps({"role": "assistant", "text": assistant_text, "timestamp": timestamp}) + "\n")