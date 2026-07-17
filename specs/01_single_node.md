# Lesson 01 — A single node (baseline)

> **Status:** implemented
> **Notebook:** `lessons/01_single_node.ipynb`
> **Graph module:** none (notebook-only baseline)

## Goal (learning)
Build and run the smallest possible LangGraph so the moving parts (`StateGraph`,
nodes, edges, `compile`, `invoke`) are concrete before anything interesting is added.

## Mechanism under test
`StateGraph`, `add_node`, `add_edge`, `START`/`END`, `compile()`, `invoke()`.

## Motivating slice of the extraction problem
Turn one transcript into one `SymptomExtraction` — the whole pipeline as a single step.

## Design
- **State:** `SymptomNoteState = {transcript, encounter_date, extraction}` (TypedDict).
- **Nodes:** `extract_clinical_data` — calls `get_extraction_model().invoke(...)`.
- **Edges:** `START → extract_clinical_data → END`. A straight line.

## Acceptance — what I must be able to observe
- [x] Graph compiles and `draw_mermaid()` shows a single linear path.
- [x] `invoke({transcript, encounter_date})` returns state with a populated `extraction`.
- [x] `show_symptom_evidence_matrix` renders the result.

## Out of scope
Any branching, looping, or state accumulation — this is the "why do I even need a
graph?" strawman that every later lesson answers.

## Notes / open questions
Deliberately underwhelming. The takeaway is that a linear single-node graph is
just a function call; lessons 02–04 justify the framework.
