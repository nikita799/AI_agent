# LangGraph lessons

A curriculum for learning LangGraph, using the clinical symptom-extraction task
(`clinical/`) as the running example. Each lesson isolates **one** LangGraph
mechanism and builds on the same schema, model, and data.

**Spec-first:** each lesson has a spec in [`../specs/`](../specs/README.md) that
defines its goal and its acceptance criteria *before* the notebook exists. Write
(or refine) the spec, then implement the notebook until every acceptance box is
checkable. You write the code — the spec is the contract, not an auto-implement input.

| # | Notebook | LangGraph mechanism | Extraction exercise |
|---|----------|---------------------|---------------------|
| 01 | `01_single_node.ipynb` ✅ | baseline: `StateGraph`, nodes, edges | `START → extract → END` |
| 02 | `02_state_and_reducers.ipynb` | `Annotated[list, add]`, `add_messages` | accumulate problems across passes instead of overwriting |
| 03 | `03_conditional_routing.ipynb` | `add_conditional_edges` | 0 problems found → route to a fallback/clarify node |
| 04 | `04_validation_loop.ipynb` ✅ | **cycles + conditional edges** | extract → validate citations → loop back & repair |
| 05 | `05_map_reduce_send.ipynb` | `Send` API, parallel superstep | fan out extraction per transcript segment, then reduce/merge |
| 06 | `06_checkpointing.ipynb` | `MemorySaver`/`SqliteSaver`, `thread_id` | resume a batch run; inspect `get_state_history` |
| 07 | `07_human_in_the_loop.ipynb` | `interrupt()` + `Command(resume=...)` | pause for a clinician to edit/approve the ledger |
| 08 | `08_tools_and_exa_search.ipynb` | `create_react_agent`, `ToolNode`, `bind_tools` | Exa web-search tool to look up an unknown drug/term |
| 09 | `09_streaming.ipynb` | `stream_mode="updates"/"values"/"messages"` | stream node progress and structured-output tokens |
| 10 | `10_subgraphs.ipynb` | subgraph-as-node | per-problem enrichment subgraph called by the parent |

✅ = scaffolded. The rest are the planned progression — build them in order, or
jump to the one whose mechanism you want next.

## Running

```bash
# one-time: install the project + deps into the venv (editable)
.venv/bin/python -m pip install -e .

# then open any lesson, launched from the repo root:
.venv/bin/jupyter lab
```

Or open a lesson in VS Code / Cursor and pick the `.venv` interpreter as the kernel
(`ipykernel` is already installed — no JupyterLab needed for that route).

Because `clinical` is installed editably, `import clinical` works in any kernel
using this venv — no `sys.path` hacks, no per-notebook `%pip install`.

## Studio (the hybrid part)

Graph-heavy lessons also ship as importable modules in `graphs/` behind
`langgraph.json`. Run `langgraph dev` from the repo root to step through them
visually. Currently wired: `validation_loop` (lesson 04).

Studio takes the graph input by hand, so to feed it a transcript grab one with the
`random-transcript` command and paste it into the `transcript` field:

```bash
random-transcript | pbcopy      # random transcript → clipboard (prints its id)
random-transcript transcript_42 | pbcopy   # a specific one
```
