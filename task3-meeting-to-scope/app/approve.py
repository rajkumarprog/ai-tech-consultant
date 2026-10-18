import hashlib
import json
import sys
import time
from pathlib import Path

STATE = Path("data/approvals.json")
OUTBOX = Path("data/outbox")


def latest(meeting):
    files = sorted(Path("data").glob(f"proposal_{meeting}_v*.md"),
                   key=lambda p: int(p.stem.rsplit("_v", 1)[1]))
    if not files:
        sys.exit("No proposal found. Run: python3 -m app.propose " + meeting)
    return files[-1]


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def state():
    return json.loads(STATE.read_text()) if STATE.exists() else {}


if __name__ == "__main__":
    cmd, meeting = sys.argv[1], sys.argv[2]
    p = latest(meeting)
    s = state()
    if cmd == "status":
        e = s.get(p.name)
        ok = bool(e) and e["sha256"] == digest(p)
        print(p.name, "| approved:", ok, "|", e["reviewer"] if e else "no reviewer")
    elif cmd == "approve":
        if len(sys.argv) < 4:
            sys.exit("Usage: approve <meeting> <reviewer name>")
        s[p.name] = {"sha256": digest(p), "reviewer": sys.argv[3],
                     "approved_at": time.strftime("%Y-%m-%d %H:%M:%S")}
        STATE.write_text(json.dumps(s, indent=1))
        print("Approved", p.name, "by", sys.argv[3])
    elif cmd == "send":
        e = s.get(p.name)
        if not e or e["sha256"] != digest(p):
            sys.exit("REFUSED: this exact version is not approved. Nothing was sent.")
        OUTBOX.mkdir(exist_ok=True)
        (OUTBOX / p.name).write_text(p.read_text())
        print("SIMULATED SEND:", p.name, "(approved by", e["reviewer"] + ")")
    else:
        sys.exit("Commands: status | approve | send")
