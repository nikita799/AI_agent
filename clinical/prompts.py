"""Prompt text for the extraction task.

The base system prompt is the one from the original ``ai_writer.ipynb`` with one
addition: excerpts must be copied VERBATIM. That single constraint is what makes
the validation loop (lesson 04) meaningful — we can mechanically check that every
cited excerpt actually appears in the transcript.
"""

EXTRACTION_SYSTEM_PROMPT = """Convert the clinical transcript into the supplied fact-ledger schema.

Rules:
1. Extract only information supported by the transcript.
2. Never infer a diagnosis from symptoms.
3. Merge repeated descriptions of the same clinical problem.
4. Attach location, character, severity, duration and modifying
   factors to the correct symptom.
5. Preserve negation, uncertainty and temporality.
6. Every `excerpt` MUST be copied VERBATIM from the transcript — an exact
   substring, not a paraphrase. Keep excerpts short (a phrase or sentence).
7. If a relationship is unclear, record it as unresolved rather
   than guessing.
8. Do not treat proposed or hypothetical events as completed events.
"""


def build_extraction_user_message(transcript: str, encounter_date: str = "not provided") -> str:
    """The first-pass human message: the transcript to extract from."""
    return f"""Encounter date: {encounter_date}

Transcript:
{transcript}
"""


def build_repair_message(unsupported: list[dict]) -> str:
    """A follow-up human message listing excerpts that failed validation.

    Used by lesson 04 when the graph loops back to re-extract: it tells the model
    exactly which citations it hallucinated so it can fix them.
    """
    lines = [
        "Some `excerpt` values you produced do NOT appear verbatim in the "
        "transcript. Re-extract, and for each characteristic use an excerpt that "
        "is an EXACT substring of the transcript. Drop any claim you cannot "
        "support with a verbatim excerpt.",
        "",
        "Excerpts that could not be found:",
    ]
    for item in unsupported:
        lines.append(f'- problem "{item["problem"]}": "{item["excerpt"]}"')
    return "\n".join(lines)


REVIEW_SYSTEM_PROMPT = """You are a second, independent clinical reviewer. Another model has already
extracted a symptom fact-ledger from the transcript. Your job is to find what it got WRONG or MISSED —
be adversarial but fair.

Rules:
1. Only flag facts actually stated in the transcript. For every `missing` item you MUST supply a
   VERBATIM excerpt (an exact substring of the transcript) that supports it.
2. Preserve negation, uncertainty and temporality. A denied symptom is `missing` only as a denied
   associated symptom, never as a present one.
3. Never invent diagnoses or facts not in the transcript.
4. Classify each issue: `missing` (not captured), `wrong` (captured but incorrect), or
   `misattributed` (attached to the wrong problem).
5. Say which problem and which schema field each change belongs to.
6. If the extraction is already complete and correct, return no changes.
"""


def build_review_user_message(transcript, extraction_json, encounter_date="not provided"):
    """The reviewer's human message: transcript + the first model's extraction to critique."""
    return f"""Encounter date: {encounter_date}

Transcript:
{transcript}

Extraction produced by the first model (JSON):
{extraction_json}

Review it. Return only concrete, transcript-supported proposed changes."""


ADJUDICATE_SYSTEM_PROMPT = """You are adjudicating a human reviewer's claim that the extraction MISSED
a symptom fact. Decide, strictly from the transcript, whether the claim is supported.

- If the transcript DOES state it: set apply=true and return a `change` with kind='missing', the
  correct problem and field, and a VERBATIM excerpt.
- If it does NOT: set apply=false and give a brief `rebuttal` (why it is not stated — a misreading,
  or only proposed/hypothetical, or actually denied).
Never invent facts. Preserve negation, uncertainty and temporality.
"""


def build_adjudicate_user_message(transcript, extraction_json, flag):
    """The adjudicator's human message: transcript + current extraction + the human's flag."""
    return f"""Transcript:
{transcript}

Current extraction (JSON):
{extraction_json}

A human reviewer claims this symptom fact was MISSED:
"{flag}"

Rule on it: is it supported by the transcript?"""
