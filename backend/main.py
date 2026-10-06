import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models.schemas import SearchRequest, SearchResponse
from services.image_search import search_images
from services.query_processor import convert_to_search_query
from services.ranking import rank_results
from services.searchapi_images import search_google_images


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "AI Image Retrieval API is running"
    }


@app.get("/test-google-images")
async def test_google_images():
    results = await search_google_images(
        "red sports car mountain road",
        limit=5,
    )
    return {
        "count": len(results),
        "results": results,
    }


@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    try:
        # 1. Convert natural language into search query
        search_query = await convert_to_search_query(
            request.prompt
        )

        if not search_query:
            raise HTTPException(
                status_code=400,
                detail="Could not create a searchable query.",
            )

        # 2. Retrieve candidates from both Unsplash and Google Images (SearchApi) concurrently
        unsplash_task = search_images(
            search_query,
            limit=10,
        )
        google_task = search_google_images(
            search_query,
            limit=10,
        )

        unsplash_res, google_res = await asyncio.gather(
            unsplash_task,
            google_task,
            return_exceptions=True,
        )

        candidates = []
        if isinstance(unsplash_res, list):
            candidates.extend(unsplash_res)
        elif isinstance(unsplash_res, Exception):
            print(f"Unsplash error: {unsplash_res}")

        if isinstance(google_res, list):
            candidates.extend(google_res)
        elif isinstance(google_res, Exception):
            print(f"Google Images (SearchApi) error: {google_res}")

        if not candidates and isinstance(unsplash_res, Exception) and isinstance(google_res, Exception):
            raise HTTPException(
                status_code=502,
                detail=f"Both image search providers failed. Unsplash: {unsplash_res}, SearchApi: {google_res}",
            )

        # 3. Handle no results
        if not candidates:
            return SearchResponse(
                original_prompt=request.prompt,
                search_query=search_query,
                results=[],
                count=0,
                message=(
                    "No relevant images were found. "
                    "Try using broader or more descriptive terms."
                ),
            )

        # 4. Rank candidates across both providers
        top_results = rank_results(
            candidates,
            search_query,
            top_k=5,
        )

        # Keep only results that have actual relevance (> 0)
        relevant_results = [
            item for item in top_results
            if item.get("relevance_score", 0) > 0
        ]

        if not relevant_results:
            return SearchResponse(
                original_prompt=request.prompt,
                search_query=search_query,
                results=[],
                count=0,
                message=(
                    "No relevant images were found. "
                    "Try using broader or more descriptive terms."
                ),
            )

        # 5. Return top relevant results
        return SearchResponse(
            original_prompt=request.prompt,
            search_query=search_query,
            results=relevant_results,
            count=len(relevant_results),
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )
