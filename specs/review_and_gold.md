# Feature — Dual-model review → human adjudication → gold dataset

> **Status:** Phase 1 complete ✅ · Phase 2 next
> **Notebook:** `workbench/review.ipynb`
> **Builds on:** `workbench/symptoms.ipynb`, `graphs/validation_loop.py`,
> `clinical.render.show_transcript_coverage`
> **Type:** feature (not a numbered lesson) — serves the extraction task; pulls in LangGraph
> (subgraphs, HITL, cycles) in Phase 3 as the task demands them.

## Goal
Turn each transcript into a trustworthy **gold** symptom extraction: **two different models**
check it and a **human adjudicates**. Model A extracts (with citation validation), Model B
reviews A's work for missed/wrong facts, the human accepts/rejects B's proposals, and the
signed-off result is saved as ground truth with full provenance. Symptoms now; extensible later.

## Distinction from the existing loop
The current `extract ⇄ validate` cycle only checks that citations are **verbatim** (mechanical,
one model). This adds a **semantic** second opinion from a **different** model, plus human sign-off.

## Flow
```
extract (Model A, validated) → review (Model B → Critique)
   → DIFF VIEW  🟩 captured by A  /  🟧 B says missed
   → human adjudicates (accept / reject / "prove it")
        nothing missing → save GOLD (+ provenance)
        something missing → apply-or-rebut (B adds it correctly, or argues why not) ⇄ human
```

## Models
- **Extractor (A):** `openai/gpt-5.6-luna` (current, `clinical.DEFAULT_MODEL`).
- **Reviewer (B):** `anthropic/claude-sonnet-5` — a **different family** for a genuine second
  opinion. Configurable via `clinical.models.REVIEWER_MODEL`.

## New pieces
- `Critique` / `ProposedChange` schema (Model B output).
- `REVIEW_SYSTEM_PROMPT` + `get_reviewer_model()`.
- `show_review_diff(transcript, extraction, critique)` — two-colour coverage highlight + proposal list.
- **(Phase 2)** adjudication cell → merge; `gold/<id>.json` with provenance. `gold/` is **gitignored**
  (contains transcript text — same privacy rule as `data/*.csv`).
- **(Phase 3)** apply-or-rebut agent + a LangGraph HITL graph.

## Phases & acceptance
### Phase 1 — Two-pass + diff view  ✅ done
- [x] `Critique` validates; the review prompt requires a **verbatim excerpt** for every `missing` item.
- [x] `show_review_diff` highlights A's excerpts (🟩) and B's proposed-missing excerpts (🟧) and lists
      B's proposals — verified with a **stub** critique + a real transcript (no LLM call).
- [x] `workbench/review.ipynb`: extract → review → diff view on a chosen transcript.

### Phase 2 — Human adjudication + save gold
- [ ] Accept/reject each proposal; accepted `missing` facts merged into the extraction.
- [ ] `gold/<transcript_id>.json`: final extraction + models used + critique + human decisions + timestamp.
- [ ] `gold/` gitignored; a dataset-progress view (how many transcripts curated).

### Phase 3 — Debate loop as a LangGraph graph (HITL)
- [ ] `graphs/review_pipeline.py`: extractor validation-loop as a **subgraph**; `interrupt()` for the
      human; the **apply-or-rebut** cycle; a checkpointer for pause/resume.

### Phase 4 — Gold as an eval set
- [ ] Re-run the extractor vs gold; report fact precision/recall + citation accuracy.

## Out of scope (for now)
- Other fact types (medications/diagnoses/…): symptoms first, but keep schemas extensible.
- Fancy UI: notebook cells are the human step in Phases 1–2; real `interrupt()` arrives in Phase 3.

## Notes
- Reviewer B must only flag facts **actually stated** (verbatim excerpt required); preserve
  negation/uncertainty/temporality; never invent diagnoses.
- Verify all non-LLM machinery (schema, diff, highlight, merge) with **stubs**; the two real model
  calls are the only cells that cost money.
