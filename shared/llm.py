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
                 "groq": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")}


class LLMUnavailable(Exception):
    pass


def _log(task, model, ms, tin, tout, ok):
    new = not LOG_PATH.exists()
    with open(LOG_PATH, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["ts", "task", "provider", "model", "latency_ms",
                        "input_tokens", "output_tokens", "ok"])
        w.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), task, PROVIDER, model,
                    int(ms), tin, tout, ok])


def complete(system: str, user: str, task: str = "misc", model: str | None = None,
             max_tokens: int = 1500) -> str:
    model = model or DEFAULT_MODEL[PROVIDER]
    start = time.time()
    try:
        if PROVIDER == "anthropic":
            if not os.getenv("ANTHROPIC_API_KEY"):
                raise LLMUnavailable("ANTHROPIC_API_KEY not set")
            from anthropic import Anthropic
            msg = Anthropic().messages.create(
                model=model, max_tokens=max_tokens, system=system,
                messages=[{"role": "user", "content": user}])
            text = msg.content[0].text
            tin, tout = msg.usage.input_tokens, msg.usage.output_tokens
        else:
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
            text = d["choices"][0]["message"]["content"]
            tin, tout = d["usage"]["prompt_tokens"], d["usage"]["completion_tokens"]
        _log(task, model, (time.time() - start) * 1000, tin, tout, True)
        return text.strip()
    except LLMUnavailable:
        raise
    except Exception as e:
        _log(task, model, (time.time() - start) * 1000, 0, 0, False)
        raise LLMUnavailable(f"{type(e).__name__}: {str(e)[:120]}")
