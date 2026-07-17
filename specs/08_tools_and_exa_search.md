# Lesson 08 — Tools & Exa search (ReAct)

> **Status:** planned
> **Notebook:** `lessons/08_tools_and_exa_search.ipynb`
> **Graph module:** `graphs/search_agent.py`

## Goal (learning)
Give the graph tools it can decide to call, and run the agentic tool-calling loop.

## Mechanism under test
`langgraph.prebuilt.create_react_agent` and/or `ToolNode` + `model.bind_tools([...])`;
the model → tools → model loop; `recursion_limit`.

## Motivating slice of the extraction problem
When the transcript mentions an unfamiliar drug or term, look it up with an **Exa
web search** tool (this is the first real use of the `exa_py` that ships unused),
so the extraction can note what it is.

## Design
- **Tools:** `exa_search(query) -> str` wrapping `exa_py` (needs `EXA_API_KEY`);
  optionally `normalize_term(term)` returning a canonical label.
- **Graph:** `create_react_agent(model, tools)` — or hand-build `agent ⇄ ToolNode`.
- **State:** message-based (`messages: Annotated[list, add_messages]`).

## Acceptance — what I must be able to observe
- [ ] For a transcript with an unknown term, the agent **chooses** to call `exa_search`
      and folds the result into its answer.
- [ ] For a transcript with nothing to look up, the tool is **not** called.
- [ ] The loop terminates (respects `recursion_limit`; no tool-call ping-pong).
- [ ] Tool functions are unit-testable in isolation (stub the HTTP call).

## Out of scope
Building a real clinical terminology database; multi-tool planning. One or two
tools, one clear decision.

## Notes / open questions
Costs real Exa + LLM calls. Gate the live cell behind a check for `EXA_API_KEY`.
Decide: prebuilt `create_react_agent` (fast) vs. hand-built `ToolNode` (more to learn).
