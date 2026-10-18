import csv
import os
import time
from pathlib import Path

import httpx
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
LOG_PATH = Path(__file__).resolve().parent / "llm_log.csv"
PROVIDER = os.getenv("LLM_PROVIDER", "anthropic")          # anthropic | groq
DEFAULT_MODEL = {"anthropic": "claude-haiku-5-5",
                 "groq": os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")}
MAX_ATTEMPTS = 4
RETRY_STATUS = {429, 500, 502, 503, 504}


class LLMUnavailable(Exception):
    pass


def _log(task, model, ms, tin, tout, ok, attempt, error=""):
    new = not LOG_PATH.exists()
    with open(LOG_PATH, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["ts", "task", "provider", "model", "attempt", "latency_ms",
                        "input_tokens", "output_tokens", "ok", "error"])
        w.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), task, PROVIDER, model, attempt,
                    int(ms), tin, tout, ok, error[:120]])


def _status(e):
    r = getattr(e, "response", None)
    return getattr(r, "status_code", None) or getattr(e, "status_code", None)


def _wait_seconds(e, attempt):
    try:
        return min(float(e.response.headers.get("retry-after")), 30)
    except Exception:
        return 2 ** attempt


def _call(system, user, model, max_tokens):
    if PROVIDER == "anthropic":
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise LLMUnavailable("ANTHROPIC_API_KEY not set")
        from anthropic import Anthropic
        msg = Anthropic().messages.create(
            model=model, max_tokens=max_tokens, system=system,
            messages=[{"role": "user", "content": user}])
        return msg.content[0].text, msg.usage.input_tokens, msg.usage.output_tokens
    if not os.getenv("GROQ_API_KEY"):
        raise LLMUnavailable("GROQ_API_KEY not set")
    r = httpx.post("https://api.groq.com/openai/v1/chat/completions",
                   headers={"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}"},
                   json={"model": model, "max_tokens": max_tokens,
                         "messages": [{"role": "system", "content": system},
                                      {"role": "user", "content": user}]},
                   timeout=60)
    r.raise_for_status()
    d = r.json()
    return (d["choices"][0]["message"]["content"] or "",
            d["usage"]["prompt_tokens"], d["usage"]["completion_tokens"])


def complete(system: str, user: str, task: str = "misc", model: str | None = None,
             max_tokens: int = 1500) -> str:
    model = model or DEFAULT_MODEL[PROVIDER]
    last = ""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        start = time.time()
        try:
            text, tin, tout = _call(system, user, model, max_tokens)
            if not text.strip():
                raise ValueError("EmptyResponse")
            _log(task, model, (time.time() - start) * 1000, tin, tout, True, attempt)
            return text.strip()
        except LLMUnavailable:
            raise
        except Exception as e:
            status = _status(e)
            last = f"{type(e).__name__} {status or ''}: {str(e)[:80]}"
            _log(task, model, (time.time() - start) * 1000, 0, 0, False, attempt, last)
            retryable = status in RETRY_STATUS or isinstance(e, (ValueError, httpx.TransportError))
            if not retryable or attempt == MAX_ATTEMPTS:
                break
            time.sleep(_wait_seconds(e, attempt))
    raise LLMUnavailable(last)
