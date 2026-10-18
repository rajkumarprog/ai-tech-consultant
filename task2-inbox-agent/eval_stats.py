import csv, json, statistics, collections

def load(p): return list(csv.DictReader(open(p)))
r1, r2 = load("../shared/llm_log_run1.csv"), load("../shared/llm_log.csv")
print("RUN 1 failed calls (429s):", sum(r["ok"] == "False" for r in r1), "of", len(r1))

by_task = collections.defaultdict(list)
for r in r2: by_task[r["task"]].append(r)
for task, rows in by_task.items():
    ok = sorted(int(r["latency_ms"]) for r in rows if r["ok"] == "True")
    print(f"RUN 2 [{task}] calls={len(rows)} ok={len(ok)} "
          f"retries={sum(int(r['attempt']) > 1 for r in rows)} "
          f"median_ms={statistics.median(ok):.0f} p95_ms={ok[max(0, int(len(ok)*.95)-1)]} "
          f"tokens_in={sum(int(r['input_tokens']) for r in rows)} "
          f"tokens_out={sum(int(r['output_tokens']) for r in rows)}")

res = json.load(open("data/results.json"))
for name, grp in (("dev", [x for x in res if x["id"] % 5], ), ("hidden", [x for x in res if x["id"] % 5 == 0])):
    print(name, "decision", sum(x["action"] == x["expect"] for x in grp), "/", len(grp))
print("decision misses:", [(x["id"], x["true_category"]) for x in res if x["action"] != x["expect"]])
