# Lesson 07 — Human-in-the-loop

> **Status:** planned
> **Notebook:** `lessons/07_human_in_the_loop.ipynb`
> **Graph module:** `graphs/human_review.py`

## Goal (learning)
Pause a running graph, hand control to a human, and resume with their input.

## Mechanism under test
`langgraph.types.interrupt()`; resuming with `Command(resume=...)`; the requirement
that a checkpointer be configured (builds on lesson 06); optionally `interrupt_before`.

## Motivating slice of the extraction problem
A clinician must review and edit the draft ledger before it's finalized — the
model proposes, the human disposes.

## Design
- **State:** `{transcript, extraction, approved}`.
- **Nodes:** `extract`; `human_review` (calls `interrupt(draft)` and returns the
  human's edited/approved extraction); `finalize`.
- **Edges:** `START → extract → human_review → finalize → END`. Compiled **with a
  checkpointer** (interrupts need one).

## Acceptance — what I must be able to observe
- [ ] `invoke` **pauses** at `human_review`; the surfaced value is the draft ledger.
- [ ] Resuming with `Command(resume=<edited extraction>)` writes the human's version
      into state and continues to `finalize`.
- [ ] The pause/resume round-trips through the checkpointer under one `thread_id`.
- [ ] (Stretch) reject path loops back to `extract` with the human's feedback.

## Out of scope
A real UI. The "human" is a notebook cell supplying the resume value.

## Notes / open questions
Confirm the current `interrupt()` API surface in the installed `langgraph` version
(it has changed across releases) — verify against `graphs/` before writing the notebook.
