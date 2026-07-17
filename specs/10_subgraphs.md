# Lesson 10 — Subgraphs

> **Status:** planned
> **Notebook:** `lessons/10_subgraphs.ipynb`
> **Graph module:** `graphs/enrichment_subgraph.py` (+ a parent graph)

## Goal (learning)
Compose graphs: use a compiled graph as a node inside another graph, and manage
the state boundary between parent and child.

## Mechanism under test
A compiled graph added as a node; shared-key vs. transformed state between
parent and subgraph; `stream(..., subgraphs=True)` to see nested execution.

## Motivating slice of the extraction problem
A reusable **per-problem enrichment** subgraph (e.g. normalize terminology →
re-validate evidence) that the parent extraction graph invokes for each problem.

## Design
- **Subgraph:** input a single `SymptomProblem`, output an enriched one; small
  internal graph (normalize → validate). Independently compilable and testable.
- **Parent:** `extract → (map problems through the subgraph) → merge`.
- **State boundary:** decide shared keys vs. an explicit wrapper node that maps
  parent↔child state; document the choice.

## Acceptance — what I must be able to observe
- [ ] The subgraph runs and is unit-testable **on its own** (one problem in, enriched
      problem out) with a stub.
- [ ] The parent composes it and produces enriched problems end-to-end.
- [ ] `stream(subgraphs=True)` shows nested parent/child steps.

## Out of scope
Recursion (a subgraph invoking itself) and cross-problem interaction. Each problem
is enriched independently.

## Notes / open questions
Cleanest when parent and child **share** the relevant state key; if not, add a thin
mapping node rather than contorting the schema. Could reuse lesson 04's validator
inside the subgraph — nice payoff for composing earlier lessons.
