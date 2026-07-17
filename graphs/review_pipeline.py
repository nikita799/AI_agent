"""Phase 3 — the review pipeline as a LangGraph graph with a human in the loop.

    START → extract → review → human_review ⟂(interrupt) → adjudicate → END

LangGraph mechanics this earns from the task:
  * **subgraph** — `extract` runs the whole lesson-04 validation loop as a nested graph;
  * **human-in-the-loop** — `human_review` calls `interrupt()` to hand control to a person,
    who resumes with `Command(resume={"accepted": [...], "flags": [...]})`;
  * **apply-or-rebut** — `adjudicate` merges the accepted reviewer proposals, then for each
    thing the human says was missed, an adjudicator model either applies it (with a verbatim
    excerpt) or returns a rebuttal;
  * **checkpointing** — required for `interrupt()`; also lets a session pause and resume.

`build_review_graph(...)` injects the three models + checkpointer so the whole thing is
testable with stubs and zero API calls. The module-level `graph` is what LangGraph Studio loads.
"""

from typing import TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from clinical import (
    ADJUDICATE_SYSTEM_PROMPT,
    REVIEW_SYSTEM_PROMPT,
    Critique,
    SymptomExtraction,
    apply_accepted,
    build_adjudicate_user_message,
    build_review_user_message,
    get_adjudicator_model,
    get_reviewer_model,
)
from graphs.validation_loop import build_graph as build_extract_graph


class ReviewState(TypedDict, total=False):
    # inputs
    transcript: str
    encounter_date: str
    # working state
    extraction: SymptomExtraction   # produced by the extract subgraph (Model A)
    critique: Critique              # produced by review (Model B)
    accepted: list                  # indices into critique.changes the human accepted
    flags: list                     # free-text "you missed X" from the human
    rebuttals: list                 # adjudicator rebuttals for rejected flags
    final_extraction: SymptomExtraction


def build_review_graph(extractor=None, reviewer=None, adjudicator=None, checkpointer=None):
    """Compile the human-in-the-loop review graph.

    Parameters (all optional — default to the real models + an in-memory checkpointer):
      extractor    — model for the validation-loop subgraph (Model A)
      reviewer     — model returning a Critique (Model B)
      adjudicator  — model returning a FlagVerdict (apply-or-rebut on human flags)
      checkpointer — required for interrupt(); MemorySaver() by default
    """
    extract_subgraph = build_extract_graph(model=extractor)   # lesson-04 loop, as a subgraph
    reviewer = reviewer if reviewer is not None else get_reviewer_model()
    adjudicator = adjudicator if adjudicator is not None else get_adjudicator_model()

    def extract(state: ReviewState) -> dict:
        """Run the whole validation-loop subgraph and lift out its extraction."""
        sub_out = extract_subgraph.invoke({
            "transcript": state["transcript"],
            "encounter_date": state.get("encounter_date", "not provided"),
        })
        return {"extraction": sub_out["extraction"]}

    def review(state: ReviewState) -> dict:
        """Model B critiques Model A's extraction."""
        messages = [
            SystemMessage(content=REVIEW_SYSTEM_PROMPT),
            HumanMessage(content=build_review_user_message(
                state["transcript"],
                state["extraction"].model_dump_json(indent=2),
                state.get("encounter_date", "not provided"),
            )),
        ]
        return {"critique": reviewer.invoke(messages)}

    def human_review(state: ReviewState) -> dict:
        """Pause for a human. Resume with {'accepted': [indices], 'flags': ['missed fact', ...]}."""
        critique = state["critique"]
        decision = interrupt({
            "extraction": state["extraction"].model_dump(),
            "proposals": [c.model_dump() for c in critique.changes],
            "overall": critique.overall,
            "instructions": "Resume with {'accepted': [indices], 'flags': ['missed fact', ...]}",
        })
        decision = decision or {}
        return {"accepted": decision.get("accepted", []), "flags": decision.get("flags", [])}

    def adjudicate(state: ReviewState) -> dict:
        """Merge accepted proposals, then apply-or-rebut each human flag."""
        extraction = state["extraction"]
        critique = state["critique"]
        accepted = [
            critique.changes[i]
            for i in state.get("accepted", [])
            if 0 <= i < len(critique.changes)
        ]
        merged, _ = apply_accepted(extraction, accepted)

        rebuttals = []
        for flag in state.get("flags", []):
            verdict = adjudicator.invoke([
                SystemMessage(content=ADJUDICATE_SYSTEM_PROMPT),
                HumanMessage(content=build_adjudicate_user_message(
                    state["transcript"], merged.model_dump_json(indent=2), flag)),
            ])
            if verdict.apply and verdict.change is not None:
                merged, _ = apply_accepted(merged, [verdict.change])
            else:
                rebuttals.append({"flag": flag, "rebuttal": verdict.rebuttal})

        return {"final_extraction": merged, "rebuttals": rebuttals}

    builder = StateGraph(ReviewState)
    builder.add_node("extract", extract)
    builder.add_node("review", review)
    builder.add_node("human_review", human_review)
    builder.add_node("adjudicate", adjudicate)

    builder.add_edge(START, "extract")
    builder.add_edge("extract", "review")
    builder.add_edge("review", "human_review")
    builder.add_edge("human_review", "adjudicate")
    builder.add_edge("adjudicate", END)

    checkpointer = checkpointer if checkpointer is not None else MemorySaver()
    return builder.compile(checkpointer=checkpointer)


# Loaded by langgraph.json for LangGraph Studio (`langgraph dev`).
graph = build_review_graph()
