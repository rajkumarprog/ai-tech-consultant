import csv
import json
import statistics
import sys
import time

import httpx

label = sys.argv[1]
cases = [json.loads(line) for line in open("evaluation/cases.jsonl")]
rows = []
for c in cases:
    start = time.time()
    try:
        r = httpx.post("http://localhost:8001/query", json={"question": c["q"]},
                       timeout=90).json()
    except Exception as e:
        r = {"status": "error:" + type(e).__name__, "sources": []}
    ms = int((time.time() - start) * 1000)
    text = " ".join(s["title"] + " " + s["url"] for s in r.get("sources", [])).lower()
    hit = any(k in text for k in c["keys"])
    if c["expect"] == "answer":
        passed = r["status"] == "answered" and hit
    else:
        passed = r["status"] == "insufficient_evidence"
    rows.append({"id": c["id"], "expect": c["expect"], "status": r["status"],
                 "source_hit": hit, "passed": passed, "latency_ms": ms, "q": c["q"]})
    time.sleep(1.5)

with open(f"evaluation/results_{label}.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)

ans = [r for r in rows if r["expect"] == "answer"]
ref = [r for r in rows if r["expect"] == "refuse"]
print(f"[{label}] answerable passed {sum(r['passed'] for r in ans)}/{len(ans)} | "
      f"refusals correct {sum(r['passed'] for r in ref)}/{len(ref)} | "
      f"median latency {statistics.median(r['latency_ms'] for r in rows)} ms")
for r in rows:
    if not r["passed"]:
        print("FAIL", r["id"], r["expect"], r["status"], "|", r["q"])
