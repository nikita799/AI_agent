"""Evidence validation: does every cited excerpt actually occur in the transcript?

This is plain, deterministic Python — no LLM, no graph. Lesson 04 wraps it in a
LangGraph node and loops back to re-extract whenever it finds hallucinated
citations. Keeping it here (and unit-testable on its own) is the whole point:
the *graph* is the thing being learned, so the graph's helpers stay simple.
"""

import re

from .schema import EVIDENCE_BACKED_FIELDS, Evidence, SymptomExtraction, SymptomProblem

# Matches transcript time markers like "[00:24]" or "00:24" so they don't cause
# spurious mismatches when an excerpt includes (or omits) the marker.
_TIMESTAMP = re.compile(r"\[?\b\d{1,2}:\d{2}\b\]?")


def normalize(text: str) -> str:
    """Lowercase, strip time markers, and collapse whitespace.

    Matching is intentionally lenient about formatting but strict about content:
    an excerpt only passes if its words really appear, in order, in the transcript.
    """
    text = _TIMESTAMP.sub(" ", text or "")
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def iter_evidence(problem: SymptomProblem):
    """Yield every ``Evidence`` attached anywhere under one problem."""
    yield from problem.core_evidence
    for field_name in EVIDENCE_BACKED_FIELDS:
        for item in getattr(problem, field_name):
            yield from item.evidence
    for associated in problem.associated_symptoms:
        yield from associated.evidence


def find_unsupported_excerpts(
    extraction: SymptomExtraction, transcript: str
) -> list[dict]:
    """Return one entry per excerpt that is NOT a verbatim substring of the transcript.

    Each entry is ``{"problem", "excerpt", "speaker", "timestamp"}`` — enough to
    show the user *and* to feed back to the model as a repair instruction.
    """
    haystack = normalize(transcript)
    unsupported: list[dict] = []

    for problem in extraction.problems:
        for evidence in iter_evidence(problem):
            needle = normalize(evidence.excerpt)
            if needle and needle not in haystack:
                unsupported.append(
                    {
                        "problem": problem.problem,
                        "excerpt": evidence.excerpt,
                        "speaker": evidence.speaker,
                        "timestamp": evidence.timestamp,
                    }
                )
    return unsupported
