from app.db import get_conn, search

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
    for q in questions:
        rows = search(conn, q, k=1)
        print(f"{rows[0]['score']:.2f}" if rows else "none", "|", q)
conn.close()
