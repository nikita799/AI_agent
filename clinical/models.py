"""Model construction, isolated from any graph.

Lessons call ``get_extraction_model()`` instead of newing up ``ChatOpenRouter``
themselves, so the model choice lives in exactly one place. ``build_graph()`` in
the lessons accepts a model argument, which makes it trivial to swap in a stub
for tests (see tests that run the graph without hitting OpenRouter).
"""

from langchain_openrouter import ChatOpenRouter

from .schema import Critique, FlagVerdict, SymptomExtraction

# The model used by the primary extraction experiment. Swap here to compare
# models across every lesson at once.
DEFAULT_MODEL = "openai/gpt-5.6-luna"


def get_chat_model(model: str = DEFAULT_MODEL, **kwargs) -> ChatOpenRouter:
    """A raw chat model (no structured output)."""
    return ChatOpenRouter(model=model, **kwargs)


def get_extraction_model(model: str = DEFAULT_MODEL, **kwargs):
    """A chat model that returns a validated ``SymptomExtraction``."""
    return get_chat_model(model, **kwargs).with_structured_output(SymptomExtraction)


# The reviewer (Model B). A DIFFERENT family from DEFAULT_MODEL so it's a genuine second
# opinion rather than the same model agreeing with itself. Swap here to try other reviewers.
REVIEWER_MODEL = "anthropic/claude-sonnet-5"


def get_reviewer_model(model: str = REVIEWER_MODEL, **kwargs):
    """A chat model that returns a validated ``Critique`` of an existing extraction."""
    return get_chat_model(model, **kwargs).with_structured_output(Critique)


def get_adjudicator_model(model: str = REVIEWER_MODEL, **kwargs):
    """A chat model that rules on a human-flagged missing fact — apply it, or rebut it."""
    return get_chat_model(model, **kwargs).with_structured_output(FlagVerdict)
