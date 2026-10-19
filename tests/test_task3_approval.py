import hashlib
import json
import sys
from pathlib import Path

TASK3 = next(
    p for p in (
        Path(__file__).resolve().parents[1] / "task3-meeting-to-scope",
        Path(__file__).resolve().parents[1] / "task3-meeting-scope",
    ) if (p / "app" / "approve.py").exists()
)
sys.path.insert(0, str(TASK3))
from app import approve


def setup(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    Path("data").mkdir(exist_ok=True)


def test_digest_sha256_length(tmp_path):
    p = tmp_path / "p.md"
    p.write_text("proposal")
    assert len(approve.digest(p)) == 64


def test_digest_hex(tmp_path):
    p = tmp_path / "p.md"
    p.write_text("proposal")
    assert all(c in "0123456789abcdef" for c in approve.digest(p))


def test_digest_matches_sha256(tmp_path):
    p = tmp_path / "p.md"
    p.write_text("proposal")
    assert approve.digest(p) == hashlib.sha256(b"proposal").hexdigest()


def test_digest_repeatable(tmp_path):
    p = tmp_path / "p.md"
    p.write_text("proposal")
    assert approve.digest(p) == approve.digest(p)


def test_digest_changes_with_content(tmp_path):
    p = tmp_path / "p.md"
    p.write_text("first")
    first = approve.digest(p)
    p.write_text("second")
    assert approve.digest(p) != first


def test_digest_changes_with_whitespace(tmp_path):
    p = tmp_path / "p.md"
    p.write_text("proposal")
    first = approve.digest(p)
    p.write_text("proposal ")
    assert approve.digest(p) != first


def test_digest_empty_file(tmp_path):
    p = tmp_path / "p.md"
    p.write_text("")
    assert approve.digest(p) == hashlib.sha256(b"").hexdigest()


def test_digest_changes_after_append(tmp_path):
    p = tmp_path / "p.md"
    p.write_text("proposal")
    first = approve.digest(p)
    p.write_text("proposal\nnew scope")
    assert approve.digest(p) != first


def test_digest_not_plain_text(tmp_path):
    p = tmp_path / "p.md"
    p.write_text("proposal")
    assert approve.digest(p) != "proposal"


def test_state_missing_file_empty(monkeypatch, tmp_path):
    setup(monkeypatch, tmp_path)
    assert approve.state() == {}


def test_state_reads_approval(monkeypatch, tmp_path):
    setup(monkeypatch, tmp_path)
    Path("data/approvals.json").write_text(
        '{"meeting_a":{"approved":true}}'
    )
    assert approve.state()["meeting_a"]["approved"] is True


def test_state_reads_multiple_records(monkeypatch, tmp_path):
    setup(monkeypatch, tmp_path)
    Path("data/approvals.json").write_text(
        json.dumps({"a": {"approved": True}, "b": {"approved": False}})
    )
    assert len(approve.state()) == 2


def test_state_empty_json(monkeypatch, tmp_path):
    setup(monkeypatch, tmp_path)
    Path("data/approvals.json").write_text("{}")
    assert approve.state() == {}


def test_state_preserves_hash(monkeypatch, tmp_path):
    setup(monkeypatch, tmp_path)
    Path("data/approvals.json").write_text(
        '{"proposal":{"hash":"abc123"}}'
    )
    assert approve.state()["proposal"]["hash"] == "abc123"


def test_latest_single_version(monkeypatch, tmp_path):
    setup(monkeypatch, tmp_path)
    p = Path("data/proposal_meeting_a_v1.md")
    p.write_text("proposal")
    assert approve.latest("meeting_a") == p


def test_latest_selects_highest_version(monkeypatch, tmp_path):
    setup(monkeypatch, tmp_path)
    for v in (1, 2, 3):
        Path(f"data/proposal_meeting_a_v{v}.md").write_text(str(v))
    assert approve.latest("meeting_a").name.endswith("_v3.md")


def test_latest_uses_numeric_order(monkeypatch, tmp_path):
    setup(monkeypatch, tmp_path)
    Path("data/proposal_meeting_a_v2.md").write_text("two")
    Path("data/proposal_meeting_a_v10.md").write_text("ten")
    assert approve.latest("meeting_a").name.endswith("_v10.md")


def test_latest_ignores_other_meeting(monkeypatch, tmp_path):
    setup(monkeypatch, tmp_path)
    Path("data/proposal_meeting_b_v9.md").write_text("other")
    Path("data/proposal_meeting_a_v1.md").write_text("target")
    assert approve.latest("meeting_a").name == "proposal_meeting_a_v1.md"


def test_latest_returns_path(monkeypatch, tmp_path):
    setup(monkeypatch, tmp_path)
    Path("data/proposal_meeting_a_v1.md").write_text("proposal")
    assert isinstance(approve.latest("meeting_a"), Path)


def test_latest_missing_proposal_stops(monkeypatch, tmp_path):
    setup(monkeypatch, tmp_path)
    try:
        approve.latest("missing")
    except SystemExit:
        return
    raise AssertionError("Expected missing proposal to stop safely")
