import os
import httpx

KB_URL = os.getenv("KB_URL", "http://localhost:8001")


def ask_kb(question: str) -> dict:
    """Call Task 1's /query. Never invent an answer if the service fails."""
    try:
        r = httpx.post(f"{KB_URL}/query", json={"question": question[:1000]}, timeout=20)
        r.raise_for_status()
        return r.json()
    except httpx.HTTPError as e:
        return {"status": "kb_unavailable", "answer": None, "sources": [],
                "needs_human": True, "reason": type(e).__name__}
