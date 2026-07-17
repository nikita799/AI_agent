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
