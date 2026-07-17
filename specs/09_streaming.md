# Lesson 09 — Streaming

> **Status:** planned
> **Notebook:** `lessons/09_streaming.ipynb`
> **Graph module:** reuse `graphs/validation_loop.py`

## Goal (learning)
Go deep on the streaming API — token-level `"messages"` and `"custom"` events, and async
`astream` — beyond the basic run-and-examine harness introduced in lesson 00
(`specs/00_run_and_inspect.md`), which already covers `"updates"`/`"values"`/`"debug"`.

## Mechanism under test
`graph.stream(input, stream_mode=...)` for `"updates"`, `"values"`, `"messages"`,
and `"custom"`; `astream` for async; `get_stream_writer()` for custom events.

## Motivating slice of the extraction problem
Stream the validation loop so each `extract`/`validate` step and each retry is
visible live, and stream the ledger's tokens as they're generated.

## Design
- **Graph:** reuse the validation loop — no new topology.
- **Cells:** one per `stream_mode`, printing what each yields and how they differ.

## Acceptance — what I must be able to observe
- [ ] `stream_mode="updates"` yields one event **per node execution** (you can see
      `extract` then `validate`, and again on a retry).
- [ ] `stream_mode="values"` yields the **cumulative state** after each step.
- [ ] `stream_mode="messages"` streams LLM **tokens** as the extraction is produced.
- [ ] A `"custom"` progress event emitted from inside a node shows up in the stream.

## Out of scope
Any front-end or transport (SSE/websocket). Printing to the notebook is enough.

## Notes / open questions
Token streaming (`"messages"`) interacts with `.with_structured_output`; verify what
actually streams for structured output in the installed version and document it.
