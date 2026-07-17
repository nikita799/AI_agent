# ai_assistant

A hands-on project with **two coequal goals**: learn LangGraph, and build a genuinely good
**clinical fact-extraction** capability. Right now the focus is pulling **symptom** facts
from Estonian consultation transcripts *well*; later it extends to other clinical-note facts
(medications, diagnoses, vitals, plan, …), so the schema is kept extensible. Work is
**notebook-centric** — you run and examine everything in `.ipynb`. LangGraph mechanics are
learned via `lessons/` (each isolating one mechanism on the shared, LangGraph-free core
`clinical/`) and pulled into the extraction pipeline as the task needs them.

## Layout

```
ai_assistant/
├── clinical/                 # stable core — imported by every lesson, NO graph code
│   ├── schema.py             # SymptomExtraction + friends (Pydantic v2, Estonian domain)
│   ├── models.py             # get_extraction_model() — ChatOpenRouter, one place to swap model
│   ├── prompts.py            # EXTRACTION_SYSTEM_PROMPT + repair-message builder
│   ├── data.py               # load_transcripts() / get_transcript() / sample_transcript()
│   ├── validation.py         # find_unsupported_excerpts() — pure, deterministic, testable
│   ├── render.py             # show_symptom_evidence_matrix / show_transcript_coverage / show_review_diff
│   ├── gold.py               # apply_accepted() merge + GoldRecord save/load (review Phase 2)
│   └── config.py             # repo-root-relative paths + .env loading
├── workbench/                # ← MAIN task notebooks: run extraction on real transcripts & examine quality
│   ├── symptoms.ipynb        # run → evidence matrix + transcript-coverage highlight → critique
│   └── review.ipynb          # dual-model: A extracts, B reviews → 🟩/🟧 diff (→ gold dataset, WIP)
├── lessons/                  # one LangGraph concept per notebook (see lessons/README.md)
│   ├── 00_run_and_inspect.ipynb  # ✅ run a graph & examine its intermediaries
│   ├── 01_single_node.ipynb  # ✅ baseline: START → extract → END
│   └── 04_validation_loop.ipynb  # ✅ first real graph: a cycle
├── graphs/                   # importable graph modules for LangGraph Studio
│   └── validation_loop.py    # build_graph(model=...) + module-level `graph`
├── data/transcripts.csv      # 105 Estonian consultation transcripts [id, transcript]
├── langgraph.json            # wires graphs/ into `langgraph dev` (Studio)
├── pyproject.toml            # installable project + deps (replaces per-notebook %pip install)
├── requirements.txt          # pinned lockfile (pip freeze)
├── .env                      # API keys (gitignored, at repo root)
├── .gitattributes            # nbstripout filter (strips notebook outputs on commit)
└── .venv/                    # Python 3.14 venv (gitignored; recreate with python3.14 -m venv .venv)
```

## Environment & running

- **The venv is `.venv/`** at the repo root (Python 3.14). Interpreter: `.venv/bin/python`.
  Recreate from scratch with `python3.14 -m venv .venv && .venv/bin/python -m pip install -e .`.
- **Install once (editable), then never `%pip install` in a notebook again:**
  ```bash
  .venv/bin/python -m pip install -e .
  ```
  This puts `clinical` and `graphs` on the path for any kernel using this venv, so
  `import clinical` works regardless of the launch directory. Deps come from
  `pyproject.toml`; exact versions are pinned in `requirements.txt`.
- **`.env`** (at the repo root, gitignored, loaded automatically when `clinical` is
  imported) holds `OPENROUTER_API_KEY`, `EXA_API_KEY`, `LANGSMITH_API_KEY`,
  `LANGSMITH_TRACING`, `LANGSMITH_PROJECT`. Real secrets — keep out of commits/output.
- **Notebooks:** `.venv/bin/jupyter lab` (from repo root). Or open the `.ipynb` in
  VS Code / Cursor and select the `.venv` interpreter (`ipykernel` is installed).
- **Studio:** `langgraph dev` from the repo root — loads graphs from `langgraph.json`.
- **Notebook outputs** are stripped on commit by `nbstripout` (git filter, see `.gitattributes`)
  so transcript text can't leak into this public repo via cell outputs. The filter
  registration lives in `.git/config` (per-clone, not committed) — after a fresh clone run
  `nbstripout --install` once (`pip install -e .` installs the tool itself).
- **LLM** = custom `ChatOpenRouter` (`langchain_openrouter`), model `openai/gpt-5.6-luna`.
  LangSmith tracing is automatic via the env vars.

## The curriculum (see `lessons/README.md`)

10 planned lessons, each adding ONE mechanism to the same extraction task: state &
reducers → conditional routing → **validation loop (cycle)** → map-reduce `Send` →
checkpointing → human-in-the-loop → tools/Exa search → streaming → subgraphs.
Scaffolded so far: **01** (single node) and **04** (validation loop).

**Lesson 04 is the reference pattern.** `graphs/validation_loop.py` builds
`START → extract → validate → (retry ↺ | END)`: `validate` checks every cited
`excerpt` is a verbatim substring of the transcript (`clinical.find_unsupported_excerpts`),
and a conditional edge loops back to `extract` — feeding the bad excerpts back to the
model — until clean or `MAX_ATTEMPTS`. `build_graph(model=...)` takes the model as an
argument so tests/notebooks can inject a stub and exercise the loop with **no LLM call**.

## Workbench (`workbench/symptoms.ipynb`) — the main task line

The task-focused notebook (not a lesson): run the citation-validated extraction on a real
transcript and examine quality inline. Two lenses:
- `show_symptom_evidence_matrix(extraction)` — the structured facts + their evidence.
- `show_transcript_coverage(transcript, extraction)` — the transcript with cited excerpts
  highlighted, so **un-highlighted text = what the extractor missed** (and non-verbatim
  citations are flagged). A final cell lists failure modes to check for.

Symptoms now; the schema and workbench are meant to extend to other clinical-note facts
(medications, diagnoses, vitals, plan, …) later.

## Spec-first workflow (`specs/`)

This repo uses a lightweight, DIY spec-driven flow (no spec-kit/framework). Every
lesson has a spec in `specs/NN_*.md` (copy `specs/TEMPLATE.md`) that states its one
learning goal and — most importantly — **observable acceptance criteria** before the
notebook is written. `specs/README.md` holds the workflow and the curriculum
"constitution" (one mechanism per lesson; reuse `clinical/`; acceptance must be
observable and ideally stub-verifiable without an LLM). Keep `Status:` in each spec
in sync with reality. **Claude should not auto-`/implement` lessons** — the user
implements them to learn; help design/plan and review against the spec's acceptance.

## Schema & domain (the `clinical` core)

- `SymptomExtraction` → `problems: list[SymptomProblem]`; each problem has evidence-backed
  lists (`quality, course, severity, onset, duration, frequency, provoking_factors,
  relieving_factors, negative_characteristics`), `associated_symptoms`, `core_evidence`.
- `EvidenceBackedText` = one atomic `text` + `evidence: list[Evidence]` (min 1).
  `Evidence` = `timestamp`, `speaker` (patient/clinician/unknown), `excerpt`.
- **Every characteristic must cite transcript evidence.** The prompt forbids inferring
  diagnoses and — new in this restructure — **requires excerpts to be verbatim** so the
  validation loop can check them mechanically.
- **Domain language is Estonian.** Field *names* are English; values/examples are Estonian
  (`laterality ∈ {vasak, parem, bilateraalne}`, `"parema alakõhu valu"`, `"ei kiirgu"`).
  Preserve this — don't "translate" the schema.
- `EVIDENCE_BACKED_FIELDS` in `schema.py` is the single source of truth for which fields
  hold evidence, so `validation.iter_evidence` can't silently miss one.

## Known issues / gotchas

- **Benign warning on import:** `UserWarning: Core Pydantic V1 functionality isn't
  compatible with Python 3.14`. Our schema is Pydantic **v2**; structured output works
  (verified). Ignore it.
- The two original experiment notebooks (`ai_writer.ipynb`, `agent.ipynb`) were removed in
  the restructure — `ai_writer.ipynb` lives on as `lessons/01_single_node.ipynb`. Their last
  committed versions are still recoverable from git history if ever needed.
