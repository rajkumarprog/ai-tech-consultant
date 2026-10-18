import json
import re
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "brain.db"


def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS pages (
        url TEXT PRIMARY KEY, content_hash TEXT,
        status TEXT, error TEXT, active INTEGER DEFAULT 1);
    CREATE VIRTUAL TABLE IF NOT EXISTS chunks USING fts5(
        url UNINDEXED, title, heading, text, images UNINDEXED);
    """)
    return conn


def save_page(conn, url, title, chunks, content_hash):
    conn.execute("DELETE FROM chunks WHERE url=?", (url,))   # no duplicates on re-run
    for c in chunks:
        conn.execute(
            "INSERT INTO chunks(url,title,heading,text,images) VALUES (?,?,?,?,?)",
            (url, title, c["heading"], c["text"], json.dumps(c["images"])))
    conn.execute(
        """INSERT INTO pages(url,content_hash,status,error,active) VALUES (?,?,'done',NULL,1)
           ON CONFLICT(url) DO UPDATE SET content_hash=excluded.content_hash,
           status='done', error=NULL, active=1""", (url, content_hash))
    conn.commit()


def mark_failed(conn, url, error):
    conn.execute(
        """INSERT INTO pages(url,status,error) VALUES (?,'failed',?)
           ON CONFLICT(url) DO UPDATE SET status='failed', error=excluded.error""",
        (url, error[:200]))
    conn.commit()


def search(conn, question, k=5):
    words = [w for w in re.findall(r"\w+", question.lower()) if len(w) > 2]
    if not words:
        return []
    return conn.execute(
        """SELECT url, title, heading, text, images, bm25(chunks) AS score
           FROM chunks
           WHERE chunks MATCH ? AND url IN (SELECT url FROM pages WHERE active=1)
           ORDER BY score LIMIT ?""", (" OR ".join(words), k)).fetchall()
