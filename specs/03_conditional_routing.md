# Lesson 03 — Conditional routing

> **Status:** planned
> **Notebook:** `lessons/03_conditional_routing.ipynb`
> **Graph module:** none

## Goal (learning)
Make the graph choose its next node at runtime based on state.

## Mechanism under test
`add_conditional_edges(source, router_fn, path_map)`; a router that returns a key
into the path map.

## Motivating slice of the extraction problem
Not every transcript contains symptoms (greetings, admin-only visits). After a
first extraction pass, **route**: findings → finalize; nothing found → a `fallback`
node that records "no clinical findings" instead of forcing empty structure.

## Design
- **State:** `{transcript, extraction, outcome}`.
- **Nodes:** `extract`; `finalize` (pass through / tidy); `fallback` (mark empty).
- **Edges:** `START → extract`; `add_conditional_edges("extract", route, {"has_problems": "finalize", "empty": "fallback"})`; both → `END`.
- **Router:** `route(state) -> "has_problems" if state["extraction"].problems else "empty"`.

## Acceptance — what I must be able to observe
- [ ] A transcript with findings reaches `finalize`; a greeting-only transcript
      reaches `fallback` (trace the path taken).
- [ ] `route` is a **pure function**, unit-tested on synthetic `SymptomExtraction`
      objects with 0 and >0 problems (no LLM).
- [ ] `draw_mermaid()` shows the branch with both labelled edges.

## Out of scope
Looping back to `extract` (that's the cycle in lesson 04). Routing here only goes
*forward* to one of several terminal nodes.

## Notes / open questions
Keep the router trivial (problem count). Resist making `fallback` clever — its job
is to prove the branch was taken.
