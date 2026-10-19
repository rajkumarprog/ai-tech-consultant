# Evaluation Report

## Task 1 — Knowledge brain

The recorded evaluation uses 24 cases: 16 answerable questions and 8 questions expected to be refused or treated as unsupported.

For `openai/gpt-oss-20b`, the recorded result was:
- Answerable cases passed: **12/16**
- Correct refusals: **8/8**
- Median latency: **653.5 ms**

Recorded failures included questions about forwarding email to Gmail, newsletter sending, shortcodes, and editing the navigation menu. One newsletter case was answered but still marked as a failure by the evaluation. These errors indicate that retrieval and answerability evaluation need further work.

The result file for the other model should be checked before reporting its exact score. Do not infer missing metrics.

## Task 2 — Inbox agent

The recorded evaluation used **50 synthetic emails**.

| Metric | `openai/gpt-oss-120b` | `openai/gpt-oss-20b` |
|---|---:|---:|
| Category correct | 48/50 | 48/50 |
| Routing/decision correct | 44/50 | 45/50 |
| Draft generation succeeded | 50/50 | 50/50 |
| Unsafe answers in the evaluated set | 0 | 0 |
| Median latency per email | 1.355 s | 0.675 s |

The commitment scan was regex-based and is not comprehensive. The dataset is synthetic and these results do not establish production safety or performance on real customer emails. Token totals and retry counts are recorded in the evaluation output files. Cost should be reported only after verifying the model pricing and the exact token accounting used.

## Task 3 — Meeting to scope

Run the Task 3 scenarios against the actual transcripts before reporting accuracy or quality scores. Verify that the repository contains the required three role-play transcripts and the follow-up to the first meeting. Do not claim that role-plays occurred unless they actually did.

## Unit tests

Latest test run: **62 passed** in 2.94 seconds. This is a local automated test result, not proof of production readiness.

```bash
python -m pytest -q
```

Report the resulting count and any failures from that fresh run. A passing unit-test suite does not replace task-specific end-to-end evaluations.

## Model comparison

The two Task 2 models were compared on the same 50-message synthetic set. The 20B model had lower measured median latency in the recorded run; the 120B model had one fewer routing/decision error. These are single recorded runs, not a controlled benchmark. Report cost only if calculated from verified pricing and recorded token usage.
