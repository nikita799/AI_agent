# specs/ — spec-first, DIY

A lightweight spec-driven workflow for this learning repo. The spec is the
contract; **you** implement it (that's the point — you're here to learn LangGraph,
not to watch an agent write it). No framework, no `/implement` automation.

## The loop

1. **Write/refine the spec** for the next lesson (copy `TEMPLATE.md`). Nail the
   *acceptance* section — that's your definition of done.
2. **Implement** the notebook (and `graphs/*.py` if graph-heavy) until every
   acceptance box is checkable.
3. **Flip `Status:` to `implemented`** and note anything that changed from the
   plan. Spec and code stay in sync.

Reach for Claude Code **plan mode** on a hard design; stop at the plan and write
the code yourself.

## Curriculum principles (the "constitution")

- **One mechanism per lesson.** If a lesson needs a second new concept to work,
  that concept belongs to an earlier lesson (or is stubbed).
- **Reuse `clinical/` for everything non-graph** (schema, model, prompts, data,
  validation, render). Lessons are ~90% graph code.
- **Acceptance must be observable, and ideally LLM-free.** Inject a stub model so
  the graph logic is provable deterministically and for free; keep at most one
  cell that calls the real model.
- **Graph-heavy lessons also ship as `graphs/*.py`** wired into `langgraph.json`,
  so they run in LangGraph Studio (`langgraph dev`).
- **Preserve the Estonian clinical domain.** Don't translate the schema.

## Index

| # | Spec | Status |
|---|------|--------|
| 01 | [single node](01_single_node.md) | implemented |
| 02 | [state & reducers](02_state_and_reducers.md) | planned |
| 03 | [conditional routing](03_conditional_routing.md) | planned |
| 04 | [validation loop](04_validation_loop.md) | implemented |
| 05 | [map-reduce with Send](05_map_reduce_send.md) | planned |
| 06 | [checkpointing](06_checkpointing.md) | planned |
| 07 | [human-in-the-loop](07_human_in_the_loop.md) | planned |
| 08 | [tools & Exa search](08_tools_and_exa_search.md) | planned |
| 09 | [streaming](09_streaming.md) | planned |
| 10 | [subgraphs](10_subgraphs.md) | planned |
