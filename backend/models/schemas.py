from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=500,
    )


class ImageResult(BaseModel):
    id: str
    title: str
    image_url: str
    thumbnail_url: str
    source_url: str
    photographer: str
    photographer_url: str
    relevance_score: float
    source: str


class SearchResponse(BaseModel):
    original_prompt: str
    search_query: str
    results: list[ImageResult]
    count: int
    message: str | None = None
