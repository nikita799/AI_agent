# Lesson 00 — Run a graph from the notebook & examine every step

> **Status:** implemented
> **Notebook:** `lessons/00_run_and_inspect.ipynb`
> **Graph module:** none new — this lesson *inspects* an existing graph
> (`graphs/validation_loop.py`)

> **Type:** foundational / toolkit. Intentionally broader than the "one mechanism per
> lesson" rule (see `specs/README.md`): it's the run-and-examine harness reused by
> every later lesson, so it introduces the handful of inspection tools together.

## Goal (learning)
Be able to run any lesson's graph from a notebook cell and **examine its intermediate
state step-by-step** — not just the final output. This is the habit that makes every
other lesson legible.

## Mechanism under test
- `graph.invoke(input)` — run to completion, inspect the final state.
- `graph.stream(input, stream_mode=...)` — watch the run unfold:
  - `"updates"` — the per-node delta (what each node changed),
  - `"values"` — the full state after each step,
  - `"debug"` — task starts/results (shows ordering and the loop).
- `clinical.show_symptom_evidence_matrix(...)` — render the final `SymptomExtraction`.
- **Where else to look:** LangSmith project `agent_01` (tracing is already on) holds the
  full trace of any real run — reference it, don't build it.

## Motivating slice of the extraction problem
The **validation loop** (`graphs/validation_loop.py`) is the richest specimen to inspect:
its retry cycle means the intermediaries actually *change* between steps — a hallucinated
excerpt gets flagged, then repaired. Watching `attempts` climb and `errors` clear is the
whole payoff, and it's invisible if you only look at the final result.

## Design
- Import `build_graph` from `graphs.validation_loop` — no new graph is written here.
- Reuse the **bad-then-good stub** from the lesson-04 tests so the loop replays
  deterministically and for free (no API cost).
- Cells (roughly one per idea):
  1. `invoke()` the graph → show final state, render the evidence matrix.
  2. `stream(stream_mode="updates")` → print each node's delta.
  3. `stream(stream_mode="values")` → print the full state after each step.
  4. `stream(stream_mode="debug")` → show task ordering / the loop.
  5. A tiny `pretty(step)` helper that summarizes a step (node, `attempts`,
     `#problems`, `#errors`) instead of dumping raw Pydantic objects.
  6. A markdown cell: open LangSmith → `agent_01` for the deep trace.

## Acceptance — what I must be able to observe
- [x] `invoke()` returns the final state and `show_symptom_evidence_matrix` renders it
      inline in the notebook.
- [x] With the bad-then-good **stub** (no LLM): `stream("updates")` prints one entry per
      node execution, and I can *see* `extract → validate` happen **twice** (the loop).
- [x] `stream("values")` shows `attempts` go `1 → 2` and `errors` go `1 → 0` across steps.
- [x] `stream("debug")` shows the four tasks in order (extract, validate, extract, validate).
- [x] Exactly **one** clearly-marked cell runs the **real** model; everything else is
      stub-driven and costs nothing.

## Out of scope
- Advanced streaming — token-level `"messages"`, `"custom"` events via
  `get_stream_writer`, `astream` — that's **lesson 09**.
- Time-travel / replaying past checkpoints via `get_state_history` — needs a
  checkpointer, that's **lesson 06**.
- Standing up LangSmith or Studio — LangSmith is only *referenced* here.

## Notes / open questions
- If you extract a reusable `pretty_stream(graph, input)` helper, it must live **outside
  `clinical/`** — that package is deliberately LangGraph-free (see the constitution). A
  `lessons/`-local module or a small separate package is the right home.
- Keep the stub identical to lesson 04's so the two lessons reinforce each other.
