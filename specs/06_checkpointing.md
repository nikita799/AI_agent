# Lesson 06 — Checkpointing & persistence

> **Status:** planned
> **Notebook:** `lessons/06_checkpointing.ipynb`
> **Graph module:** reuse `graphs/validation_loop.py`

## Goal (learning)
Persist graph state so a run can be inspected, resumed, and survive a restart.

## Mechanism under test
`compile(checkpointer=...)` with `MemorySaver` then `SqliteSaver`; `thread_id` in
the `config`; `graph.get_state(config)` and `graph.get_state_history(config)`.

## Motivating slice of the extraction problem
Batch-process transcripts where a run might be interrupted; resume the same
`thread_id` instead of restarting, and inspect what happened at each step.

## Design
- **State / nodes:** reuse the validation-loop graph — no new graph logic, just a
  checkpointer.
- **Runs:** invoke with `config={"configurable": {"thread_id": "t1"}}`; simulate an
  interruption; re-invoke the same thread.

## Acceptance — what I must be able to observe
- [ ] `get_state_history` returns one checkpoint per superstep, newest first.
- [ ] Re-invoking an existing `thread_id` **resumes** from the last checkpoint
      rather than starting over (observe attempts/state carried over).
- [ ] `SqliteSaver` state survives a **fresh Python process** (MemorySaver does not).
- [ ] Demonstrable with a stub model.

## Out of scope
Using a checkpoint to *pause for a human* — that's lesson 07 (which requires this).

## Notes / open questions
`SqliteSaver` lives in `langgraph.checkpoint.sqlite` (separate extra). Confirm it's
installed, or fall back to `MemorySaver` + a note. Write the sqlite file under a
gitignored path.
