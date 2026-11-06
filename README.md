# AI Tech Consultant

Three connected Python prototypes that automate common customer-support and pre-sales work, with a human kept in the loop for anything risky:

1. **Knowledge Brain** – a FastAPI service that answers support questions from ingested help-center articles, cites its sources, and refuses when the evidence is weak.
2. **Inbox Agent** – classifies incoming emails, looks up answers through the Knowledge Brain API, drafts replies, and lets a human approve, edit or reject them in a Streamlit review UI.
3. **Meeting to Scope** – turns meeting transcripts into structured requirements, effort estimates and a proposal, detects scope changes between meetings, and locks approved proposals with a content hash.

## Results (recorded runs)

| What was measured | Result |
|---|---|
| Unit tests | **62 passed** (`pytest`) |
| Inbox Agent – email category accuracy (50 synthetic emails) | **48/50** |
| Inbox Agent – routing decision accuracy | 44–45/50 depending on model |
| Knowledge Brain – correct refusals on unanswerable questions | **8/8** |
| Knowledge Brain – answerable questions passed (gpt-oss-20b) | 12/16 |

Details and limitations are in [EVALS.md](EVALS.md). Datasets are synthetic; these are prototype results, not production benchmarks.

## Tech stack

Python · FastAPI · Pydantic · Streamlit · SQLite · httpx · pytest · LLM APIs (Groq `gpt-oss` models; Anthropic optional)

## Getting started

```bash
git clone https://github.com/rajkumarprog/ai-tech-consultant.git
cd ai-tech-consultant

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add a Groq API key (free tier available at [console.groq.com](https://console.groq.com/)).

**Run the tests** (no API key needed):

```bash
python -m pytest -q
```

**Build the Knowledge Brain index first** (crawls public help-center articles into a local SQLite full-text index; about 1 second per article):

```bash
cd task1-knowledge-brain
python -m app.ingest --limit 100     # increase the limit for more coverage
cd ..
```

Without this step the API starts but escalates every question, because the index is empty.

**Start the Knowledge Brain API and the Inbox review UI together** (macOS / Linux / Codespaces):

```bash
./run.sh
```

- Knowledge Brain API docs: http://localhost:8001/docs
- Inbox review UI: http://localhost:8501

Or start them separately:

```bash
cd task1-knowledge-brain && uvicorn app.main:app --port 8001
cd task2-inbox-agent && streamlit run review_app.py
```

**Meeting to Scope** (command line):

```bash
cd task3-meeting-to-scope
python -m app.extract data/transcripts/meeting_a.txt
```

A dev container is included, so the project also opens in GitHub Codespaces.

## Project structure

```
shared/llm.py               # one LLM client for all tasks: retries, backoff, call logging
task1-knowledge-brain/      # ingestion, relevance filtering, /query API, expert escalation loop
task2-inbox-agent/          # classify -> look up -> draft -> human review, plus evaluation scripts
task3-meeting-to-scope/     # extract, feasibility, estimate, propose, diff, approve
tests/                      # pytest unit tests for all three tasks
DESIGN.md  EVALS.md  AI_LOG.md
```

## Design highlights

- **Refuse instead of guess:** answers are generated only when retrieved evidence passes a relevance check
- **Human approval gates:** drafts and scope changes need human sign-off; edits after approval are detected by hashing the proposal
- **Safe autonomy:** the inbox agent only auto-handles a low-risk category after a streak of unchanged human approvals; any edit resets it
- **Resilient LLM calls:** bounded retries with backoff on rate limits and server errors, and every call logged with latency and token counts

See [DESIGN.md](DESIGN.md) for the full design notes and known limitations.

## Author

**Rajkumar Panikera** · [LinkedIn](https://www.linkedin.com/in/rajkumar-panikera-a083ab1a5) · [GitHub](https://github.com/rajkumarprog)
