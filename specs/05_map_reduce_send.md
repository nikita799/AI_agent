# Lesson 05 — Map-reduce with `Send`

> **Status:** planned
> **Notebook:** `lessons/05_map_reduce_send.ipynb`
> **Graph module:** `graphs/map_reduce.py`

## Goal (learning)
Fan work out across a dynamic number of parallel branches in one superstep, then
reduce the results — the map-reduce shape.

## Mechanism under test
`langgraph.constants.Send` returned from an edge/router; parallel superstep
execution; a reducer (`Annotated[list, add]`) to collect the branch outputs.

## Motivating slice of the extraction problem
Split a long transcript into segments (or take a batch of transcripts), extract
each **in parallel**, then merge/dedupe into a single ledger.

## Design
- **State:** `{transcript, segments, extractions: Annotated[list[SymptomExtraction], add], merged}`.
- **Nodes:** `split` (chunk the transcript); `extract_segment` (one segment →
  partial extraction); `merge` (concat + dedupe problems into `merged`).
- **Edges:** `split` returns `[Send("extract_segment", {"segment": s}) for s in segments]`;
  all fan-ins → `merge → END`.

## Acceptance — what I must be able to observe
- [ ] N segments → N `extract_segment` invocations in **one** superstep (count via a
      stub model's call counter; optionally confirm the fan-out in a LangSmith trace).
- [ ] `merge` produces one `SymptomExtraction`; duplicate problems across segments
      are deduped.
- [ ] Provable with a stub model (deterministic partial extractions per segment).

## Out of scope
Re-fanning based on results (recursive map-reduce) and per-branch validation loops
(compose with lesson 04 later).

## Notes / open questions
Segmentation strategy is a distraction — split naïvely (by `[mm:ss]` blocks or fixed
size). The lesson is `Send` + reduce, not chunking quality.
