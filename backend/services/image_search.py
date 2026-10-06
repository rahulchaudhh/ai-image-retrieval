import os

import httpx
from dotenv import load_dotenv

load_dotenv()

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
UNSPLASH_SEARCH_URL = "https://api.unsplash.com/search/photos"


async def search_images(query: str, limit: int = 20) -> list[dict]:
    if not UNSPLASH_ACCESS_KEY:
        raise RuntimeError("UNSPLASH_ACCESS_KEY is not configured")

    headers = {
        "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
    }

    params = {
        "query": query,
        "per_page": min(limit, 30),
        "page": 1,
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(
            UNSPLASH_SEARCH_URL,
            headers=headers,
            params=params,
        )

    response.raise_for_status()

    data = response.json()

    results = []

    for photo in data.get("results", []):
        results.append({
            "id": photo["id"],
            "title": photo["alt_description"] or "Untitled image",
            "image_url": photo["urls"]["regular"],
            "thumbnail_url": photo["urls"]["small"],
            "source_url": photo["links"]["html"],
            "photographer": photo["user"]["name"],
            "photographer_url": photo["user"]["links"]["html"],
            "source": "Unsplash",
        })

    return results
