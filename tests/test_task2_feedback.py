import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "task2-inbox-agent"))
import feedback


def setup_db(monkeypatch, tmp_path):
    monkeypatch.setattr(feedback, "DB_PATH", tmp_path / "test_inbox.db")


def test_normalize_lowercases():
    assert feedback.normalize("HELLO") == "hello"


def test_normalize_collapses_spaces():
    assert feedback.normalize("hello   world") == "hello world"


def test_normalize_trims_spaces():
    assert feedback.normalize(" hello ") == "hello"


def test_normalize_none():
    assert feedback.normalize(None) == ""


def test_empty_database_has_no_autonomy(monkeypatch, tmp_path):
    setup_db(monkeypatch, tmp_path)
    assert not feedback.may_auto_send("how_to")


def test_one_approval_starts_streak(monkeypatch, tmp_path):
    setup_db(monkeypatch, tmp_path)
    state = feedback.record(1, "how_to", "Hello", "Hello", "sent")
    assert state["streak"] == 1


def test_nineteen_approvals_not_enough(monkeypatch, tmp_path):
    setup_db(monkeypatch, tmp_path)
    for i in range(19):
        feedback.record(i, "how_to", "Hello", "Hello", "sent")
    assert not feedback.may_auto_send("how_to")


def test_twenty_approvals_enable_how_to(monkeypatch, tmp_path):
    setup_db(monkeypatch, tmp_path)
    for i in range(20):
        feedback.record(i, "how_to", "Hello", "Hello", "sent")
    assert feedback.may_auto_send("how_to")


def test_edit_resets_streak(monkeypatch, tmp_path):
    setup_db(monkeypatch, tmp_path)
    for i in range(5):
        feedback.record(i, "how_to", "Hello", "Hello", "sent")
    state = feedback.record(6, "how_to", "Hello", "Edited", "sent")
    assert state["streak"] == 0


def test_edit_revokes_autonomy(monkeypatch, tmp_path):
    setup_db(monkeypatch, tmp_path)
    for i in range(20):
        feedback.record(i, "how_to", "Hello", "Hello", "sent")
    feedback.record(21, "how_to", "Hello", "Edited", "sent")
    assert not feedback.may_auto_send("how_to")


def test_rejection_resets_streak(monkeypatch, tmp_path):
    setup_db(monkeypatch, tmp_path)
    feedback.record(1, "how_to", "Hello", "", "rejected")
    assert not feedback.may_auto_send("how_to")


def test_refunds_never_auto_send(monkeypatch, tmp_path):
    setup_db(monkeypatch, tmp_path)
    for i in range(25):
        feedback.record(i, "refund_cancel", "Hello", "Hello", "sent")
    assert not feedback.may_auto_send("refund_cancel")


def test_complaints_never_auto_send(monkeypatch, tmp_path):
    setup_db(monkeypatch, tmp_path)
    for i in range(25):
        feedback.record(i, "complaint", "Hello", "Hello", "sent")
    assert not feedback.may_auto_send("complaint")


def test_categories_have_separate_streaks(monkeypatch, tmp_path):
    setup_db(monkeypatch, tmp_path)
    for i in range(10):
        feedback.record(i, "how_to", "Hello", "Hello", "sent")
        feedback.record(i, "complaint", "Hello", "Hello", "sent")
    assert not feedback.may_auto_send("how_to")
    assert not feedback.may_auto_send("complaint")


def test_case_difference_counts_unchanged(monkeypatch, tmp_path):
    setup_db(monkeypatch, tmp_path)
    state = feedback.record(1, "how_to", "HELLO", "hello", "sent")
    assert state["streak"] == 1


def test_whitespace_difference_counts_unchanged(monkeypatch, tmp_path):
    setup_db(monkeypatch, tmp_path)
    state = feedback.record(1, "how_to", "a  b", "a b", "sent")
    assert state["streak"] == 1


def test_edited_draft_not_unchanged(monkeypatch, tmp_path):
    setup_db(monkeypatch, tmp_path)
    state = feedback.record(1, "how_to", "Draft", "Changed", "sent")
    assert state["streak"] == 0


def test_rejection_revokes_autonomy(monkeypatch, tmp_path):
    setup_db(monkeypatch, tmp_path)
    for i in range(20):
        feedback.record(i, "how_to", "Hello", "Hello", "sent")
    feedback.record(21, "how_to", "Hello", "", "rejected")
    assert not feedback.may_auto_send("how_to")


def test_unknown_category_not_autonomous(monkeypatch, tmp_path):
    setup_db(monkeypatch, tmp_path)
    assert not feedback.may_auto_send("unknown")


def test_normalize_punctuation_preserved():
    assert feedback.normalize("Hello!") == "hello!"


def test_rejected_identical_text_does_not_count(monkeypatch, tmp_path):
    setup_db(monkeypatch, tmp_path)
    state = feedback.record(1, "how_to", "Hello", "Hello", "rejected")
    assert state["streak"] == 0
