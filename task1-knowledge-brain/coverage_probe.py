import re
from app.db import get_conn, search

STOP = {
    "the", "what", "how", "can", "does", "and", "for", "with",
    "that", "this", "are", "you", "your", "from", "have", "has",
    "was", "will", "why", "when", "where", "which", "who", "use",
    "using", "get", "make", "send", "give"
}

def words(text):
    return {
        w.rstrip("s")
        for w in re.findall(r"\w+", text.lower())
        if len(w) > 2 and w not in STOP
    }

def best_coverage(question, rows):
    q_words = words(question)
    if not q_words:
        return 0.0

    best = 0.0
    for row in rows:
        chunk_words = words(
            row["title"] + " " + row["heading"] + " " + row["text"]
        )
        best = max(best, len(q_words & chunk_words) / len(q_words))
    return best

good = [
    "Can I send a mass email campaign?",
    "How do I create an email account?",
    "How do I set up a payment gateway?",
    "How do I change my website logo?",
    "How do I add a member?"
]

bad = [
    "What is the capital of France?",
    "Who won the cricket world cup?",
    "Give me a recipe for pasta",
    "How tall is Mount Everest?",
    "What is the weather today?"
]

conn = get_conn()
for label, questions in (("SHOULD ANSWER", good), ("SHOULD REFUSE", bad)):
    print("\n" + label)
    for question in questions:
        score = best_coverage(question, search(conn, question, k=5))
        print(f"{score:.2f} | {question}")
conn.close()
