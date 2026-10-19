# AI Usage Log

This log distinguishes prompts reconstructed from the visible development conversation from verbatim prompt records. Model-call telemetry is recorded separately in `shared/llm_log.csv`.

## Five useful development prompts

The following are concise paraphrases of requests made during development, not guaranteed verbatim quotations from the original conversation.

1. **Task 1 — Knowledge Brain:** Build a Python support knowledge system using the Brilliant Directories support sitemap, with cited answers and honest abstention when evidence is insufficient.
   - **Outcome:** Implemented ingestion/retrieval and query handling. Smoke tests included a newsletter question and an unrelated question that returned insufficient evidence.

2. **Task 1 — Evaluation:** Test answerable and unanswerable support questions and compare two model configurations.
   - **Outcome:** Added a 24-case evaluation and recorded model results in `EVALS.md`.

3. **Task 2 — Inbox agent:** Build an email classification and reply-drafting workflow that calls the Task 1 API, supports human review, and avoids unsupported commitments.
   - **Outcome:** Implemented classification, drafting, a review interface, and synthetic-email evaluations. The interface simulates sending rather than sending real email.

4. **Task 2 — Feedback and autonomy:** Implement review feedback and a consecutive-approval threshold before allowing category-level auto-send.
   - **Outcome:** Added feedback/streak logic and tests. The prototype should not be treated as a production email service.

5. **Task 3 — Scope and change control:** Extract meeting requirements, check whether platform configuration may satisfy them, estimate effort, compare follow-up requirements with a baseline, and require human approval.
   - **Outcome:** Implemented feasibility, estimation, change-report, and approval workflows. Only the two transcript files currently present are documented as inputs.

## Rejected AI answer

- **Historical rejection:** No exact rejected AI answer has yet been verified from the available development record.
- **Reason:** The model-call CSV records task, model, timing, token counts, and success status, but does not preserve the complete prompt and response text.
- **What was done instead:** No historical rejection is fabricated here. A genuine rejected answer and its correction must be added if recoverable from the conversation history or another contemporaneous record. If it cannot be recovered, disclose this limitation to the evaluator and ask whether a clearly labelled retrospective example is acceptable.

## Evidence and limitations

- Automated tests: 62 passed in the latest recorded local run.
- `shared/llm_log.csv` contains model-call telemetry; it is not a full prompt/response transcript.
- The email dataset is synthetic.
- Only `meeting_a.txt` and `meeting_c.txt` are currently present. This does not establish that three friend role-plays were conducted.
- Paraphrased prompts above are not verbatim historical quotations.
