

from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent / "data" / "emails.jsonl"

with DATA_PATH.open("r", encoding="utf-8") as f:
    emails = {
        email["id"]: email
        for email in map(json.loads, f)
        if email.get("id") is not None
    }
import json
from pathlib import Path

import streamlit as st

import feedback

st.set_page_config(page_title="Inbox review", layout="wide")

BASE_DIR = Path(__file__).resolve().parent
EMAILS_PATH = BASE_DIR / "data" / "emails.jsonl"
RESULTS_PATH = BASE_DIR / "data" / "results.json"


def load_jsonl(path):
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def load_results():
    with RESULTS_PATH.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError("results.json must contain a JSON list.")
    return data


try:
    emails = {e["id"]: e for e in load_jsonl(EMAILS_PATH)}
    results = load_results()
except (OSError, ValueError, json.JSONDecodeError, KeyError) as exc:
    st.error(f"Could not load inbox data: {exc}")
    st.stop()

results_by_id = {r["id"]: r for r in results if "id" in r}
available_ids = [i for i in results_by_id if i in emails]

st.title("Inbox Agent: review drafts")
st.caption("Sending is simulated. No real email leaves this app.")

if not available_ids:
    st.warning("No matching emails and results were found.")
    st.stop()

selected_id = st.sidebar.selectbox(
    "Email",
    available_ids,
    format_func=lambda i: f"#{i} {emails[i].get('subject', 'No subject')}",
)

result = results_by_id[selected_id]
email = emails[selected_id]
category = result.get("category", "unknown")
action = result.get("action", "escalate")
draft = (result.get("reply") or "").strip()
draft_ok = bool(result.get("draft_ok")) and bool(draft)
escalation_required = action == "escalate"

left, right = st.columns(2)

with left:
    st.subheader("Customer email")
    st.write(f"**{email.get('subject', 'No subject')}**")
    st.write(email.get("body", "No email body provided."))
    st.write(
        f"Category: `{category}` | Risk: `{result.get('risk', 'unknown')}` "
        f"| Route: `{action}`"
    )

    if escalation_required:
        st.warning(
            "Human response required. This email cannot be marked as sent "
            "through the simulated-answer workflow."
        )

    sources = result.get("sources") or []
    if sources:
        st.subheader("Knowledge sources")
        for source in sources:
            title = source.get("title", "Knowledge article")
            url = source.get("url", "")
            if url.startswith(("https://", "http://")):
                st.markdown(f"- [{title}]({url})")
            else:
                st.write(f"- {title} (no valid source URL)")
    else:
        st.info("No knowledge sources were attached to this result.")

with right:
    st.subheader("Draft reply")

    if not draft_ok:
        st.error(
            "No usable draft is available. Generate or write a draft before "
            "approving it."
        )
        if result.get("error"):
            st.caption(f"Draft error: {result['error']}")

    edited_text = st.text_area(
        "Review and edit the reply",
        value=draft,
        height=280,
        key=f"reply_{selected_id}",
        disabled=not draft_ok,
    )

    unchanged = bool(draft_ok) and edited_text.strip() == draft

    if draft_ok and not escalation_required:
        st.caption(
            "Draft unchanged." if unchanged
            else "Draft edited. Approval will reset the unchanged streak."
        )

    send_col, reject_col = st.columns(2)

    with send_col:
        send_clicked = st.button(
            "Approve (simulated send)",
            disabled=not draft_ok or escalation_required
            or not edited_text.strip(),
            use_container_width=True,
        )

    with reject_col:
        reject_clicked = st.button(
            "Reject draft",
            disabled=not draft_ok,
            use_container_width=True,
        )

    if send_clicked:
        state = feedback.record(
            selected_id,
            category,
            draft,
            edited_text.strip(),
            "sent",
            model=result.get("model", "openai/gpt-oss-120b"),
            prompt_version=result.get("prompt_version", "draft-v1"),
        )
        st.success(
            f"Approval recorded (simulated only). "
            f"Unchanged streak for {category}: {state['streak']}."
        )

    if reject_clicked:
        state = feedback.record(
            selected_id,
            category,
            draft,
            edited_text.strip(),
            "rejected",
            model=result.get("model", "openai/gpt-oss-120b"),
            prompt_version=result.get("prompt_version", "draft-v1"),
        )
        st.warning(
            f"Draft rejected. Unchanged streak for {category}: "
            f"{state['streak']}."
        )

st.sidebar.subheader("Autonomy status")
conn = feedback.get_conn()
try:
    rows = conn.execute(
        "SELECT category, streak, autonomous FROM category_state ORDER BY category"
    ).fetchall()
    if not rows:
        st.sidebar.caption("No approval history recorded yet.")
    for row in rows:
        st.sidebar.write(
            f"{row['category']}: streak {row['streak']}, "
            f"auto-send {'ON' if row['autonomous'] else 'off'}"
        )
finally:
    conn.close()


import json
from pathlib import Path

import streamlit as st

# Locate data relative to this Python file
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "emails.jsonl"

st.set_page_config(
    page_title="AI Inbox Agent",
    page_icon="📧",
    layout="wide",
)

st.title("AI Inbox Agent")
st.caption("Review email classifications and AI-generated reply drafts.")

# Load emails safely
if not DATA_PATH.is_file():
    st.error(f"Email data file was not found: {DATA_PATH}")
    st.info(
        "Please ensure that task2-inbox-agent/data/emails.jsonl "
        "exists in the GitHub repository."
    )
    st.stop()

emails = {}

try:
    with DATA_PATH.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            email = json.loads(line)
            email_id = email.get("id")

            if email_id is not None:
                emails[email_id] = email

except (OSError, json.JSONDecodeError) as error:
    st.error(f"Could not load the email data: {error}")
    st.stop()

if not emails:
    st.warning("No emails were found in the data file.")
    st.stop()

email_ids = list(emails.keys())

selected_id = st.sidebar.selectbox(
    "Select an email",
    email_ids,
    format_func=lambda email_id: str(email_id),
)

email = emails[selected_id]

st.subheader(f"Email: {selected_id}")

st.write("**Subject**")
st.write(email.get("subject", "No subject provided"))

st.write("**From**")
st.write(email.get("from", email.get("sender", "Unknown sender")))

st.write("**Email content**")
body = email.get("body", email.get("text", email.get("content", "")))
st.write(body if body else "No email content provided.")

st.divider()

st.subheader("Classification and review")

for field in ("category", "classification", "priority", "decision"):
    if field in email:
        st.write(f"**{field.replace('_', ' ').title()}:** {email[field]}")

draft = (
    email.get("draft")
    or email.get("draft_reply")
    or email.get("reply")
    or email.get("suggested_reply")
    or ""
)

st.write("**Suggested reply**")

edited_draft = st.text_area(
    "Review or edit the reply before taking action",
    value=str(draft),
    height=180,
    key=f"draft_{selected_id}",
)

col1, col2 = st.columns(2)

with col1:
    if st.button("Approve draft", use_container_width=True):
        st.session_state[f"review_{selected_id}"] = "Approved"
        st.success("Draft approved for review. No email was sent.")

with col2:
    if st.button("Reject draft", use_container_width=True):
        st.session_state[f"review_{selected_id}"] = "Rejected"
        st.warning("Draft rejected. No email was sent.")

review_status = st.session_state.get(f"review_{selected_id}")

if review_status:
    st.info(f"Current review status: {review_status}")

st.caption(
    "Demo mode: review actions are simulated. "
    "This application does not send real emails."
)


