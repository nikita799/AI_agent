# Lesson 02 — State & reducers

> **Status:** planned
> **Notebook:** `lessons/02_state_and_reducers.ipynb`
> **Graph module:** none

## Goal (learning)
Understand how LangGraph merges each node's returned dict into state, and how a
**reducer** changes that merge from "overwrite" to "combine".

## Mechanism under test
`Annotated[list[...], operator.add]` reducers; `langgraph.graph.message.add_messages`;
the default last-write-wins channel behaviour.

## Motivating slice of the extraction problem
Run extraction in **two passes** (e.g. first half of the transcript, then the
second) and accumulate the problems found, instead of the second pass clobbering
the first.

## Design
- **State:** `problems: Annotated[list[SymptomProblem], operator.add]`;
  optionally `messages: Annotated[list, add_messages]`.
- **Nodes:** `extract_first`, `extract_second` — each returns `{"problems": [...]}`.
- **Edges:** `START → extract_first → extract_second → END` (sequential is enough
  to show the merge; parallelism is lesson 05).

## Acceptance — what I must be able to observe
- [ ] With the `add` reducer, final `problems` contains items from **both** nodes.
- [ ] Remove the reducer (plain `list`) → the second node **overwrites** the first
      (observe the difference explicitly — this is the whole lesson).
- [ ] `add_messages` dedupes/merges by message id when the same message is re-emitted.
- [ ] All observable with a **stub model** (no LLM call).

## Out of scope
Parallel writes (`Send`, lesson 05) and loops (lesson 04). Reducers matter *most*
under concurrency, but sequential writes are enough to see the mechanism.

## Notes / open questions
Decide whether to also show a **custom reducer** (e.g. dedupe problems by
`(problem, laterality)`) — good stretch, but keep the core demo to `add`.
