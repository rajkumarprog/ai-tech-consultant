import re
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "inbox.db"
THRESHOLD = 20                       # unchanged sends in a row
AUTONOMY_ALLOWED = {"how_to"}        # high-risk categories never go automatic


def get_conn():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS interactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email_id INTEGER, category TEXT, draft TEXT, final_text TEXT,
        outcome TEXT, unchanged INTEGER, model TEXT, prompt_version TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS category_state (
        category TEXT PRIMARY KEY, streak INTEGER DEFAULT 0,
        autonomous INTEGER DEFAULT 0);
    """)
    return conn


def normalize(text):
    return re.sub(r"\s+", " ", text or "").strip().lower()


def record(email_id, category, draft, final_text, outcome,
           model="none", prompt_version="v0"):
    """outcome: 'sent' (human sent it) or 'rejected' (human discarded the draft)."""
    unchanged = outcome == "sent" and normalize(draft) == normalize(final_text)
    conn = get_conn()
    conn.execute(
        "INSERT INTO interactions(email_id, category, draft, final_text, outcome, "
        "unchanged, model, prompt_version) VALUES (?,?,?,?,?,?,?,?)",
        (email_id, category, draft, final_text, outcome, int(unchanged),
         model, prompt_version))
    conn.execute("INSERT OR IGNORE INTO category_state(category) VALUES (?)", (category,))
    if unchanged:
        conn.execute("UPDATE category_state SET streak = streak + 1 WHERE category=?",
                     (category,))
    else:                                # any edit or rejection resets AND revokes
        conn.execute("UPDATE category_state SET streak = 0, autonomous = 0 WHERE category=?",
                     (category,))
    streak = conn.execute("SELECT streak FROM category_state WHERE category=?",
                          (category,)).fetchone()["streak"]
    if streak >= THRESHOLD and category in AUTONOMY_ALLOWED:
        conn.execute("UPDATE category_state SET autonomous = 1 WHERE category=?", (category,))
    conn.commit()
    state = dict(conn.execute("SELECT * FROM category_state WHERE category=?",
                              (category,)).fetchone())
    conn.close()
    return state


def may_auto_send(category):
    conn = get_conn()
    row = conn.execute("SELECT autonomous FROM category_state WHERE category=?",
                       (category,)).fetchone()
    conn.close()
    return bool(row and row["autonomous"]) and category in AUTONOMY_ALLOWED
