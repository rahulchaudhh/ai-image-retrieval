import json
import os
import re

import httpx
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = os.getenv(
    "ANTHROPIC_MODEL",
    "claude-haiku-4-5",
)
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"


def fallback_query(prompt: str) -> str:
    """
    Simple fallback if Claude is unavailable.
    """
    query = prompt.strip()

    remove_phrases = [
        "show me",
        "find me",
        "search for",
        "give me",
        "i want",
        "i need",
        "an image of",
        "a picture of",
    ]

    for phrase in remove_phrases:
        query = re.sub(
            rf"\b{re.escape(phrase)}\b",
            "",
            query,
            flags=re.IGNORECASE,
        )

    return " ".join(query.split())


async def convert_to_search_query(prompt: str) -> str:
    """
    Use Claude to convert a natural-language prompt
    into a concise visual search query.
    """

    if not ANTHROPIC_API_KEY:
        return fallback_query(prompt)

    system_prompt = """
You convert natural-language image requests into concise search queries.

Rules:
- Return ONLY a JSON object.
- Use this exact format:
  {"search_query": "..."}
- Keep important visual concepts.
- Remove conversational wording such as "find me", "show me", etc.
- Normalize grammar into natural image-search keywords.
- Preserve important objects, people, actions, locations, colors,
  brands, and visual context.
- Do not invent details that are not present.
- Keep the query between 3 and 12 meaningful words.

Example:
User: "find me a man playing PS5 on sofa drinking coke"
Output:
{"search_query":"man playing PS5 on sofa drinking Coca-Cola"}
"""

    payload = {
        "model": ANTHROPIC_MODEL,
        "max_tokens": 100,
        "system": system_prompt,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
    }

    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                ANTHROPIC_URL,
                headers=headers,
                json=payload,
            )

        response.raise_for_status()

        data = response.json()
        text = data["content"][0]["text"].strip()

        # Handle accidental markdown code fences
        text = re.sub(r"^```json\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

        parsed = json.loads(text)

        query = parsed.get("search_query", "").strip()

        if query:
            return query

    except Exception:
        pass

    # Keep the application usable if Claude fails
    return fallback_query(prompt)
