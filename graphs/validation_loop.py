"""Lesson 04 — the first *real* graph: a cycle.

    START -> extract -> validate -> (loop back to extract | END)

`extract` runs the LLM; `validate` checks that every cited excerpt is a verbatim
substring of the transcript; the conditional edge loops back to `extract` (with
the hallucinated excerpts fed back in) until the citations are clean or we hit
`MAX_ATTEMPTS`.

LangGraph concepts this isolates:
  * a **cycle** (an edge that points backwards) — the reason to use a graph at
    all rather than a linear chain;
  * **conditional edges** (`add_conditional_edges`) to decide loop vs. finish;
  * **state that carries across supersteps** (`attempts`, `errors`).

`build_graph(model=...)` takes the model as an argument so tests can inject a
stub and exercise the loop deterministically without calling OpenRouter. The
module-level `graph` is what `langgraph.json` loads for LangGraph Studio.
"""

from typing import TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from clinical import (
    EXTRACTION_SYSTEM_PROMPT,
    SymptomExtraction,
    build_extraction_user_message,
    build_repair_message,
    find_unsupported_excerpts,
    get_extraction_model,
)

MAX_ATTEMPTS = 3


class ValidationState(TypedDict, total=False):
    # inputs
    transcript: str
    encounter_date: str
    # working state
    extraction: SymptomExtraction
    errors: list[dict]  # excerpts that failed validation on the last pass
    attempts: int  # how many times `extract` has run


def build_graph(model=None, max_attempts: int = MAX_ATTEMPTS):
    """Compile the validation-loop graph.

    Parameters
    ----------
    model:
        Anything with ``.invoke(messages) -> SymptomExtraction``. Defaults to the
        real structured-output model; pass a stub in tests.
    max_attempts:
        How many times ``extract`` may run before we give up and return the
        best-effort extraction anyway.
    """
    model = model if model is not None else get_extraction_model()

    def extract(state: ValidationState) -> dict:
        """Run the LLM. On a retry, tell it which excerpts it hallucinated."""
        messages = [
            SystemMessage(content=EXTRACTION_SYSTEM_PROMPT),
            HumanMessage(
                content=build_extraction_user_message(
                    state["transcript"],
                    state.get("encounter_date", "not provided"),
                )
            ),
        ]
        previous_errors = state.get("errors")
        if previous_errors:
            messages.append(HumanMessage(content=build_repair_message(previous_errors)))

        extraction = model.invoke(messages)
        return {"extraction": extraction, "attempts": state.get("attempts", 0) + 1}

    def validate(state: ValidationState) -> dict:
        """Flag any cited excerpt that is not a verbatim substring of the transcript."""
        errors = find_unsupported_excerpts(state["extraction"], state["transcript"])
        return {"errors": errors}

    def route(state: ValidationState) -> str:
        """The loop decision: finish clean, give up, or try again."""
        if not state["errors"]:
            return "ok"
        if state.get("attempts", 0) >= max_attempts:
            return "give_up"
        return "retry"

    builder = StateGraph(ValidationState)
    builder.add_node("extract", extract)
    builder.add_node("validate", validate)

    builder.add_edge(START, "extract")
    builder.add_edge("extract", "validate")
    builder.add_conditional_edges(
        "validate",
        route,
        {"ok": END, "give_up": END, "retry": "extract"},  # <- the cycle
    )

    return builder.compile()


# Loaded by langgraph.json for LangGraph Studio (`langgraph dev`).
graph = build_graph()
