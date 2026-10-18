import json
import sqlite3

import streamlit as st

import feedback

st.set_page_config(page_title="Inbox review", layout="wide")
emails = {e["id"]: e for e in map(json.loads, open("data/emails.jsonl"))}
results = json.load(open("data/results.json"))

st.title("Inbox Agent: review drafts")
st.caption("Sending is simulated: no real email leaves this app.")

sel = st.sidebar.selectbox(
    "Email", [r["id"] for r in results],
    format_func=lambda i: f"#{i} {emails[i]['subject']}")
r = next(x for x in results if x["id"] == sel)
e = emails[sel]

left, right = st.columns(2)
with left:
    st.subheader("Customer email")
    st.write(f"**{e['subject']}**")
    st.write(e["body"])
    st.write(f"Category: `{r['category']}` | Risk: `{r.get('risk')}` | "
             f"Route: `{r['action']}`")
    if r["action"] == "escalate":
        st.warning("Policy: a human must answer this kind of email.")
    for s in r.get("sources", []):
        st.markdown(f"- [{s['title']}]({s['url']})")

with right:
    st.subheader("Draft reply")
    if not r["draft_ok"]:
        st.error(f"Draft failed: {r['error']}. Write your own reply.")
    draft = r.get("reply") or ""
    final = st.text_area("Edit if needed", draft, height=260, key=f"t{sel}")
    c1, c2 = st.columns(2)
    if c1.button("Send (simulated)"):
        state = feedback.record(sel, r["category"], draft, final, "sent",
                                model="openai/gpt-oss-120b", prompt_version="draft-v1")
        st.success(f"Recorded. Unchanged streak for {r['category']}: {state['streak']}")
    if c2.button("Reject draft"):
        state = feedback.record(sel, r["category"], draft, final, "rejected",
                                model="openai/gpt-oss-120b", prompt_version="draft-v1")
        st.info("Draft rejected. Streak reset.")

st.sidebar.subheader("Autonomy status")
conn = feedback.get_conn()
for row in conn.execute("SELECT * FROM category_state"):
    st.sidebar.write(f"{row['category']}: streak {row['streak']}, "
                     f"auto-send {'ON' if row['autonomous'] else 'off'}")
conn.close()
