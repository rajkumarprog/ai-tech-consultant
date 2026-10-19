# Design Notes — AI Tech Consultant

## 1. Goals and boundaries

The repository contains three related workflow prototypes. The shared business principle is to use AI to accelerate routine work while retaining explicit boundaries around unsupported claims and consequential actions. The system is a prototype, not a production deployment.

## 2. Task 1: support knowledge brain

The ingestion pipeline retrieves support content and stores material for later retrieval. The query path uses relevance filtering before passing evidence to the answer component. This is intended to reduce unsupported answers: when relevant evidence is insufficient, the system should abstain or use its configured fallback rather than invent platform behavior.

Answers should expose source references so a reviewer can inspect the evidence. Retrieval quality is a key dependency: an answer model cannot reliably cite an article that was not ingested or retrieved. Query phrasing, chunking, stale pages, and the relevance threshold can all affect recall. The current evaluation results include answerable cases that did not pass, so this remains an area for improvement.

## 3. Task 2: inbox agent

The inbox pipeline classifies incoming messages, selects an action, consults the Task 1 API where appropriate, and generates a proposed reply. A review interface allows a human to inspect and edit or reject the draft. The evaluation uses 50 synthetic messages, so its results measure behavior on that dataset only.

Feedback is recorded by category. The autonomy logic tracks consecutive unchanged approvals and permits autonomy only for the configured low-risk category. Edits and rejections reset the streak. This is a prototype policy: before production, the threshold logic must be enforced at the actual send boundary, tested under concurrency, and supported by stronger monitoring and a reliable rollback mechanism. The current UI's send action is simulated.

## 4. Task 3: meeting to scope

The pipeline extracts requirements from meeting transcripts, evaluates whether existing platform functionality may satisfy a request, estimates work in low/likely/high hours, and prepares a proposal. A follow-up meeting is compared with a baseline to identify unchanged, modified, removed, and added requirements.

A human should resolve ambiguity and approve material scope changes. The proposal approval flow hashes the proposal content so edits can be detected after approval. A real deployment would also need authenticated reviewer identity, durable audit events, secure storage, and transactional handling of approval and delivery.

## 5. Model and prompt boundaries

Model outputs are untrusted data and must be validated before downstream use. Prefer structured schemas and explicit allowed actions over free-form instructions. Email text, transcript content, and retrieved articles may contain malicious or irrelevant instructions; these must be treated as input data, not system instructions. API keys belong in local environment configuration and must never be committed.

## 6. Failure handling and operational risks

External model APIs can rate-limit, time out, or return malformed output. Retries should be bounded and use backoff. A fallback must be distinguishable from a successful model answer. Logs should not expose secrets or unnecessary personal data. Production use would require authentication, authorization, rate limiting, retention rules, monitoring, and backup/recovery.

## 7. Known limitations

- Evaluation samples are small and Task 2 emails are synthetic.
- Retrieval failures can cause abstentions or missed answerable questions.
- Regex-based commitment checks are not a complete safety guarantee.
- Human review and simulated sending do not constitute a production mail integration.
- Estimates are planning aids, not contractual commitments.
- Test results cover only the assertions exercised by the test suite.
