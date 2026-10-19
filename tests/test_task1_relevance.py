import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] /
                       "task1-knowledge-brain" / "app"))

from relevance import words, coverage, relevant_rows


def row(title="Member management", heading="Add members",
        text="Administrators can add members from the dashboard."):
    return {"title": title, "heading": heading, "text": text}


def test_words_lowercases():
    assert "member" in words("Member")


def test_words_removes_punctuation():
    assert "member" in words("member!")


def test_words_ignores_common_stop_words():
    assert "the" not in words("the member")


def test_words_ignores_short_words():
    assert "to" not in words("to add")


def test_words_returns_set():
    assert isinstance(words("member member"), set)


def test_words_normalizes_plural_s():
    assert "member" in words("members")


def test_coverage_exact_match():
    assert coverage("members dashboard", row()) == 1.0


def test_coverage_no_match():
    assert coverage("airplane spaceship", row()) == 0.0


def test_coverage_empty_question():
    assert coverage("", row()) == 0.0


def test_coverage_stop_words_only():
    assert coverage("how can you", row()) == 0.0


def test_coverage_is_between_zero_and_one():
    score = coverage("members dashboard airplane", row())
    assert 0.0 <= score <= 1.0


def test_relevant_rows_returns_matching_row():
    r = row()
    assert relevant_rows("members dashboard", [r]) == [r]


def test_relevant_rows_excludes_unrelated_row():
    assert relevant_rows("airplane spaceship", [row()]) == []


def test_relevant_rows_empty_input():
    assert relevant_rows("members dashboard", []) == []


def test_relevant_rows_empty_question():
    assert relevant_rows("", [row()]) == []


def test_relevant_rows_preserves_order():
    a = row(title="Member management")
    b = row(title="Member settings")
    result = relevant_rows("members dashboard", [a, b])
    assert result == [a, b]


def test_coverage_title_contributes():
    assert coverage("newsletter", row(title="Newsletter", heading="", text="")) == 1.0


def test_coverage_heading_contributes():
    assert coverage("newsletter", row(title="", heading="Newsletter", text="")) == 1.0


def test_coverage_text_contributes():
    assert coverage("newsletter", row(title="", heading="", text="Newsletter")) == 1.0


def test_relevant_rows_rejects_below_threshold():
    r = row(title="Members", heading="", text="")
    assert coverage("members airplane", r) < 0.7
    assert relevant_rows("members airplane", [r]) == []


def test_duplicate_query_words_do_not_inflate_coverage():
    assert coverage("members members dashboard", row()) == 1.0
