from typing import Dict, Any

from services.collaborative import get_cf_recommendations
from services.llm_fallback import get_llm_recommendations


def get_best_recommendations(book_name: str, pt, books, similarity_scores) -> Dict[str, Any]:
    """
    Try collaborative filtering first; if empty, try LLM fallback.
    Returns dict with keys:
      - source: 'cf' | 'llm'
      - items: list of recommendation dicts
    """
    cf_items = get_cf_recommendations(book_name, pt, books, similarity_scores)
    if cf_items:
        return {"source": "cf", "items": cf_items}

    llm_items = get_llm_recommendations(book_name)
    if llm_items:
        return {"source": "llm", "items": llm_items}

    return {"source": "none", "items": []}


