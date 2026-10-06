import os
import httpx
from dotenv import load_dotenv

load_dotenv()

SEARCHAPI_KEY = os.getenv("SEARCHAPI_KEY")
SEARCHAPI_URL = "https://www.searchapi.io/api/v1/search"


async def search_google_images(
    query: str,
    limit: int = 10,
) -> list[dict]:
    """Search Google Images through SearchApi.io."""
    if not SEARCHAPI_KEY:
        raise RuntimeError("SEARCHAPI_KEY is not configured")

    headers = {
        "Authorization": f"Bearer {SEARCHAPI_KEY}",
        "Accept": "application/json",
    }
    params = {
        "engine": "google_images",
        "q": query,
        "page": 1,
        "hl": "en",
        "gl": "us",
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(
            SEARCHAPI_URL,
            headers=headers,
            params=params,
        )
        response.raise_for_status()
        data = response.json()

    results = []
    for index, item in enumerate(
        data.get("images", [])[:limit],
        start=1,
    ):
        original = item.get("original", {})
        source = item.get("source", {})
        image_url = original.get("link")
        source_url = source.get("link")

        if not image_url or not source_url:
            continue

        thumbnail_url = item.get("thumbnail") or image_url

        # Instagram & Facebook block hotlinking from external websites.
        # Use Google's reliable cached thumbnail URL so they never break.
        source_name = (source.get("name") or "").lower()
        url_lower = image_url.lower()
        if any(host in url_lower or host in source_name for host in ["instagram", "facebook", "fbcdn"]):
            if thumbnail_url:
                image_url = thumbnail_url

        results.append({
            "id": f"google-{index}-{image_url}",
            "title": item.get("title") or "Untitled image",
            "image_url": image_url,
            "thumbnail_url": thumbnail_url,
            "source_url": source_url,
            "photographer": source.get("name") or "Web source",
            "photographer_url": source_url,
            "source": "Google Images",
        })

    return results
