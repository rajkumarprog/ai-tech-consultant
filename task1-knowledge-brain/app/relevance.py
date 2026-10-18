import re

STOP = {
    "the", "what", "how", "can", "does", "and", "for", "with",
    "that", "this", "are", "you", "your", "from", "have", "has",
    "was", "will", "why", "when", "where", "which", "who",
    "use", "using", "get", "make", "send", "give"
}

MIN_COVERAGE = 0.7

def words(text):
    return {
        w.rstrip("s")
        for w in re.findall(r"\w+", text.lower())
        if len(w) > 2 and w not in STOP
    }

def coverage(question, row):
    q = words(question)
    if not q:
        return 0.0
    chunk = words(
        row["title"] + " " + row["heading"] + " " + row["text"]
    )
    return len(q & chunk) / len(q)

def relevant_rows(question, rows):
    return [
        r for r in rows
        if coverage(question, r) >= MIN_COVERAGE
    ]
