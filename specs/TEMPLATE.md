# Lesson NN — <title>

> **Status:** planned | implemented
> **Notebook:** `lessons/NN_<name>.ipynb`
> **Graph module (if graph-heavy):** `graphs/<name>.py`

## Goal (learning)
<!-- ONE sentence: which LangGraph mechanism this lesson exists to teach. If you
     can't name it in one sentence, the lesson is doing too much. -->

## Mechanism under test
<!-- The specific API(s), by name: e.g. `langgraph.constants.Send`,
     `add_conditional_edges`, `interrupt()`, `MemorySaver`. -->

## Motivating slice of the extraction problem
<!-- 1–2 sentences: why this mechanism is a natural fit for the clinical task.
     The clinical problem serves the lesson, never the other way around. -->

## Design
- **State:** <!-- fields + reducers, e.g. `problems: Annotated[list, add]` -->
- **Nodes:** <!-- each node and what it does -->
- **Edges:** <!-- the graph shape, including conditionals/loops -->

## Acceptance — what I must be able to observe
<!-- Concrete, checkable observations. These double as tests. Prefer ones you can
     verify WITHOUT an LLM (stub the model), so the graph logic is provable and free.
     e.g.
     - [ ] N segments → N parallel extract calls in one superstep
     - [ ] give-up path caps at max_attempts (no infinite loop)
     - [ ] router is a pure function, unit-testable in isolation -->

## Out of scope
<!-- What this lesson deliberately does NOT do, and which later lesson owns it. -->

## Notes / open questions
<!-- Anything you're unsure about — resolve before implementing, or note the risk. -->
