import json
import time

from classify import ESCALATE_CATEGORIES, classify
from draft import make_draft
from kb_client import ask_kb

emails = [json.loads(line) for line in open("data/emails.jsonl")]
results = []

for e in emails:
    start = time.time()
    category = classify(e["subject"], e["body"])
    kb, action = None, "escalate"
    if category not in ESCALATE_CATEGORIES and category != "unknown":
        kb = ask_kb(e["subject"])                   # v2: subject-only query
        if kb["status"] == "answered":
            action = "answer"
    d = make_draft(e, category, kb if action == "answer" else None)
    results.append({
        "id": e["id"], "true_category": e["category"], "category": category,
        "expect": e["expect"], "action": action,
        "kb_status": kb["status"] if kb else None,
        "draft_ok": d["ok"], "reply": d.get("reply"), "summary": d.get("summary"),
        "risk": d.get("risk"), "sources": d.get("sources", []),
        "error": d.get("error"), "latency_s": round(time.time() - start, 2)})
    print(e["id"], category, action, "draft_ok" if d["ok"] else "DRAFT_FAILED")
    time.sleep(1.5)

json.dump(results, open("data/results.json", "w"), indent=1)
n = len(results)
print("\ncategory correct:", sum(r["category"] == r["true_category"] for r in results), "/", n)
print("decision correct:", sum(r["action"] == r["expect"] for r in results), "/", n)
print("drafts ok:", sum(r["draft_ok"] for r in results), "/", n)
print("unsafe (answered but expected escalate):",
      sum(r["action"] == "answer" and r["expect"] == "escalate" for r in results))
