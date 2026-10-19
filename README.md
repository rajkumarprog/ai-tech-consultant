# AI Tech Consultant

Three connected prototypes for support knowledge retrieval, inbox triage, and meeting-to-scope workflows.

## Setup

Use Python 3.11+ (or the version used to develop this repository), create a virtual environment, install the dependencies from the project's dependency files, and configure the required API key in a local `.env` file. Never commit `.env` or real customer data.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

**Before relying on the commands above:** verify the dependency file and required environment variable names in this repository. If dependencies are defined separately per task, install those task-specific requirements instead.

## Components

- **Task 1 — Knowledge brain:** ingests support content and retrieves relevant source passages for answers.
- **Task 2 — Inbox agent:** classifies email, consults the Task 1 API, drafts responses, and provides a human-review workflow.
- **Task 3 — Meeting to scope:** extracts meeting requirements, estimates work, builds proposals, compares follow-up scope, and uses a hash-based approval gate.

## Running

Run each task using its own documented entry point and configuration. Task 2 depends on the Task 1 API being available. Check each task's source files and command-line help before running; this README does not claim that a single-command launcher has been verified.

## Safety and limitations

The included email dataset is synthetic. Evaluation scores are not proof of production readiness. Review generated answers, estimates, and scope changes before use. The inbox UI's send action is simulated; do not treat this prototype as a production email-sending system.

See [DESIGN.md](DESIGN.md), [EVALS.md](EVALS.md), and [AI_LOG.md](AI_LOG.md).
