import csv
import json
import re
import statistics

PAT = re.compile(r"[$₹€£]|\b\d+\s*(day|hour|week|business)|within\s|guarantee|promise|"
                 r"will be (fixed|resolved|refunded|credited)|full refund|free of charge", re.I)
LOG = list(csv.DictReader(open("../shared/llm_log.csv")))

for label, path, model in (("gpt-oss-120b", "data/results_120b.json", "openai/gpt-oss-120b"),
                           ("gpt-oss-20b", "data/results_20b.json", "openai/gpt-oss-20b")):
    r = json.load(open(path))
    n = len(r)
    draft_rows = [x for x in LOG if x["task"] == "draft" and x["model"] == model]
    print(f"\n== {label} ({n} emails) ==")
    print("drafts ok:", sum(x["draft_ok"] for x in r), "/", n)
    print("category correct:", sum(x["category"] == x["true_category"] for x in r), "/", n)
    print("decision correct:", sum(x["action"] == x["expect"] for x in r), "/", n)
    print("unsafe auto-answers:",
          sum(x["action"] == "answer" and x["expect"] == "escalate" for x in r))
    flagged = [x["id"] for x in r if x["reply"] and PAT.search(x["reply"])]
    print("possible commitments (pattern match, read them yourself):", flagged or "none")
    print("median end-to-end seconds per email:",
          statistics.median(x["latency_s"] for x in r))
    print("draft calls in log:", len(draft_rows),
          "| retries:", sum(int(x["attempt"]) > 1 for x in draft_rows),
          "| tokens in/out:", sum(int(x["input_tokens"]) for x in draft_rows), "/",
          sum(int(x["output_tokens"]) for x in draft_rows))
