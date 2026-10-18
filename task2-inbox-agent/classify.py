# Order matters: the first matching category wins.
RULES = [
    ("refund_cancel", ["refund", "cancel", "chargeback", "money back",
                       "delete all my data", "cheaper plan", "dispute the charge"]),
    ("complaint", ["unacceptable", "broke our", "losing customers", "rude",
                   "misled", "was down for", "vanished", "nobody"]),
    ("quote_request", ["how much", "what would it cost", "price", "quote", "package"]),
    ("project_request", ["can you build", "can you add", "can you connect",
                         "we would like", "we want", "support spanish"]),
    ("follow_up", ["did you get", "any update", "following up", "checking in",
                   "thanks, i tried", "did you receive"]),
    ("troubleshooting", ["not ", "cannot", "fail", "error", "slow", "broken",
                         "does nothing", "still shows", "no results", "charged twice"]),
    ("how_to", ["how do i", "how can i", "where do i", "can i ", "where is"]),
]

ESCALATE_CATEGORIES = {"refund_cancel", "complaint", "quote_request",
                       "project_request", "follow_up"}


def classify(subject: str, body: str) -> str:
    text = f"{subject} {body}".lower()
    for category, keywords in RULES:
        if any(k in text for k in keywords):
            return category
    return "unknown"
