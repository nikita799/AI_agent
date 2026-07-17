# Lesson 04 — Validation loop (first cycle)

> **Status:** implemented
> **Notebook:** `lessons/04_validation_loop.ipynb`
> **Graph module:** `graphs/validation_loop.py`

## Goal (learning)
Build the first *real* graph — one with an edge that points backwards — and see why
that's the thing a linear chain can't do.

## Mechanism under test
Cycles (backward edge); `add_conditional_edges` for the loop decision; state that
carries across supersteps (`attempts`, `errors`).

## Motivating slice of the extraction problem
An evidence ledger is only trustworthy if every cited `excerpt` really appears in
the transcript. Extract → validate citations → loop back and repair hallucinated
ones until clean or `MAX_ATTEMPTS`.

## Design
- **State:** `{transcript, encounter_date, extraction, errors, attempts}`.
- **Nodes:** `extract` (on retry, feeds prior errors back via `build_repair_message`);
  `validate` (`clinical.find_unsupported_excerpts`).
- **Edges:** `START → extract → validate`; `add_conditional_edges("validate", route,
  {"ok": END, "give_up": END, "retry": "extract"})` — `retry` is the cycle.
- **Injection:** `build_graph(model=None, max_attempts=MAX_ATTEMPTS)` takes the
  model as an argument so tests can pass a stub.

## Acceptance — what I must be able to observe
- [x] Stub that hallucinates once then fixes itself → model called 2×, `attempts == 2`,
      `errors == []` (the loop ran exactly once, then exited).
- [x] Always-hallucinating stub with `max_attempts=2` → capped at 2 calls, 1 error
      retained (no infinite loop).
- [x] Validator is pure/deterministic: good excerpt → `[]`, invented excerpt → flagged.
- [x] `draw_mermaid()` shows the `validate -.retry.-> extract` back-edge.

## Out of scope
Persistence across process restarts (lesson 06) and pausing for a human to fix
citations manually (lesson 07).

## Notes / open questions
Depends on the **verbatim-excerpt** rule in `clinical/prompts.py`; loosening it back
to "preserve meaning" makes validation fail on paraphrase (a good thing to demo).
