"""
ai/memory_parser.py
"""

from ai.client import client

MEMORY_TOOL = [
    {
        "name": "extract_memory",
        "description": "Extracts a fact the user wants remembered, categorizing it.",
        "input_schema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": ["identity", "goals", "interests", "technical", "preferences", "knowledge", "projects", "lifestyle"],
                    "description": "Which category this fact belongs to.",
                },
                "key": {
                    "type": "string",
                    "description": "A short label for this fact (e.g. 'school', 'favorite_language'). Not used for 'projects'.",
                },
                "value": {
                    "type": "string",
                    "description": "The actual fact/value to remember.",
                },
            },
            "required": ["category", "key", "value"],
        },
    }
]


def extract_memory(text: str) -> dict:
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=150,
        system=(
            "Extract a fact the user wants remembered about themselves, and categorize it. "
            "Categories: identity (who they are - school, job, name), goals (what they're working toward), "
            "interests (hobbies, things they like), technical (skills, tools, languages they use), "
            "preferences (likes/dislikes, settings), knowledge (things they know/have learned), "
            "projects (things they're building - use this category with a descriptive key like the project name), "
            "lifestyle (routines, habits, daily life details)."
        ),
        tools=MEMORY_TOOL,
        tool_choice={"type": "tool", "name": "extract_memory"},
        messages=[{"role": "user", "content": text}],
    )

    for block in response.content:
        if block.type == "tool_use":
            return block.input