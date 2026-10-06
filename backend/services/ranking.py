import re
from difflib import SequenceMatcher


STOPWORDS = {
    "a", "an", "the", "of", "on", "in", "at", "to",
    "for", "with", "and", "or", "is", "are", "this",
    "that", "me", "my", "please"
}


def tokenize(text: str) -> list[str]:
    return [
        word
        for word in re.findall(r"[a-zA-Z0-9]+", text.lower())
        if word not in STOPWORDS
    ]


def normalize_word(word: str) -> str:
    """
    Very small normalization for common word variations.
    """
    if word.endswith("ing") and len(word) > 5:
        return word[:-3]

    if word.endswith("ed") and len(word) > 4:
        return word[:-2]

    if word.endswith("s") and len(word) > 4:
        return word[:-1]

    return word


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def score_result(query: str, result: dict) -> float:
    query_tokens = [
        normalize_word(word)
        for word in tokenize(query)
    ]

    text = result.get("title", "")
    candidate_tokens = [
        normalize_word(word)
        for word in tokenize(text)
    ]

    if not query_tokens or not candidate_tokens:
        return 0.0

    score = 0.0

    # Exact / normalized token matches
    for query_word in query_tokens:
        if query_word in candidate_tokens:
            score += 1.0
            continue

        # Fuzzy match for things like:
        # play -> playing
        # car -> cars
        best_match = max(
            similarity(query_word, candidate_word)
            for candidate_word in candidate_tokens
        )

        if best_match >= 0.75:
            score += 0.5

    # Phrase match bonus
    normalized_query = " ".join(query_tokens)
    normalized_candidate = " ".join(candidate_tokens)

    if normalized_query in normalized_candidate:
        score += 2.0

    # Normalize to roughly 0-1
    maximum = len(query_tokens) + 2.0

    return min(score / maximum, 1.0)


def rank_results(
    results: list[dict],
    query: str,
    top_k: int = 5,
) -> list[dict]:

    scored_results = []

    for result in results:
        score = score_result(query, result)

        result_copy = {
            **result,
            "relevance_score": round(score, 3),
        }

        scored_results.append(result_copy)

    scored_results.sort(
        key=lambda item: item["relevance_score"],
        reverse=True,
    )

    return scored_results[:top_k]
