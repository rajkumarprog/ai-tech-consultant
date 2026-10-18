import json
from classify import classify, ESCALATE_CATEGORIES
from kb_client import ask_kb

emails = [json.loads(line) for line in open("data/emails.jsonl")]


def decide(email):
    category = classify(email["subject"], email["body"])
    if category in ESCALATE_CATEGORIES or category == "unknown":
        return category, "escalate", None
    kb = ask_kb(f"{email['subject']}. {email['body']}")
    if kb["status"] in ("answered", "retrieval_only"):
        return category, "answer", kb
    return category, "escalate", kb


def is_hidden(email_id):          # ids ending in 0 or 5 = hidden test set
    return email_id % 5 == 0


stats = {"dev": [0, 0, 0], "hidden": [0, 0, 0]}   # total, class correct, decision correct
for e in emails:
    category, action, kb = decide(e)
    s = stats["hidden" if is_hidden(e["id"]) else "dev"]
    s[0] += 1
    s[1] += category == e["category"]
    s[2] += action == e["expect"]
    if category != e["category"] or action != e["expect"]:
        print(f"MISS id={e['id']:>2} true={e['category']}/{e['expect']} "
              f"got={category}/{action} | {e['subject']}")

for name, (total, cls, dec) in stats.items():
    print(f"{name}: {total} emails | category {cls}/{total} | decision {dec}/{total}")
