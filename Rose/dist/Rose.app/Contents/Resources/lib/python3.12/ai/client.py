"""
ai/client.py

The shared Anthropic client instance. Kept separate from llm.py specifically
to avoid circular imports - llm.py depends on plugins/, and several
ai/ files need the client without needing plugins/ at all.
"""

import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()