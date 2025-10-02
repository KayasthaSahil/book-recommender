import os
import json
from typing import List, Dict

from dotenv import load_dotenv

try:
    # LangChain + Google Generative AI
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.schema import HumanMessage, SystemMessage
except Exception:
    ChatGoogleGenerativeAI = None
    HumanMessage = None
    SystemMessage = None


load_dotenv(override=False)


def _extract_json(text: str) -> List[Dict]:
    """Best-effort extraction of JSON array from LLM text response."""
    try:
        return json.loads(text)
    except Exception:
        pass

    # Try to find code block
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            try:
                return json.loads(part)
            except Exception:
                continue

    # Fallback empty
    return []


def get_llm_recommendations(book_title: str, max_results: int = 7) -> List[Dict]:
    """
    Ask Gemini via LangChain for 5-7 relevant book recommendations for the given title.
    Returns a list of dicts with keys: title, author, description.
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return []

    if ChatGoogleGenerativeAI is None:
        return []

    try:
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        llm = ChatGoogleGenerativeAI(model=model_name, api_key=api_key, temperature=0.4)

        sys_prompt = (
            "You are a helpful book recommendation engine. "
            "Given an input book title, suggest 5-7 similar or thematically related books. "
            "Respond ONLY as a JSON array where each item has keys: 'title', 'author', 'description'. "
            "Keep descriptions short (<= 30 words). Do not include any extra commentary."
        )

        user_prompt = (
            f"Input book title: {book_title}\n"
            f"Return up to {max_results} recommendations."
        )

        messages = [
            SystemMessage(content=sys_prompt),
            HumanMessage(content=user_prompt)
        ]

        response = llm(messages)
        text = response.content if hasattr(response, "content") else str(response)
        items = _extract_json(text)

        normalized: List[Dict] = []
        for item in items[:max_results]:
            if not isinstance(item, dict):
                continue
            title = str(item.get("title", "")).strip()
            author = str(item.get("author", "")).strip() or "Unknown"
            description = str(item.get("description", "")).strip()
            if not title:
                continue
            normalized.append({
                "title": title,
                "author": author,
                "description": description
            })

        return normalized
    except Exception:
        return []


