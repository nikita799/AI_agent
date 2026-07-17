"""The clinical fact-ledger schema.

This is the stable heart of the project and is deliberately kept free of any
LangGraph code: every lesson imports these types but builds its *own* graph
around them. The domain language is Estonian (see CLAUDE.md) — preserve it.
"""

from typing import Literal

from pydantic import BaseModel, Field


class Evidence(BaseModel):
    timestamp: str | None = Field(
        default=None,
        description="Timestamp from the transcript, e.g. '00:24'.",
    )
    speaker: Literal["patient", "clinician", "unknown"] = Field(
        description="Source of the information."
    )
    excerpt: str = Field(
        description=(
            "A short, VERBATIM excerpt copied from the transcript that supports "
            "the extracted information. Copy the wording exactly (the validation "
            "lesson checks that each excerpt really occurs in the transcript)."
        )
    )


class EvidenceBackedText(BaseModel):
    text: str = Field(
        description=(
            "One atomic characteristic of the parent symptom, "
            "without additional interpretation."
        )
    )
    evidence: list[Evidence] = Field(
        min_length=1,
        description="Evidence supporting this specific characteristic.",
    )


class AssociatedSymptom(BaseModel):
    symptom: str = Field(
        description=(
            "Concise name of a symptom assessed in relation to the parent problem."
        )
    )
    status: Literal["present", "denied", "uncertain"] = Field(
        description=(
            "Whether the associated symptom is present, explicitly denied, "
            "or uncertain."
        )
    )
    evidence: list[Evidence] = Field(
        default_factory=list,
        description="Evidence supporting the status of this associated symptom.",
    )


class SymptomProblem(BaseModel):
    problem: str = Field(
        description=(
            "The main symptom or complaint defining this clinical problem, "
            "for example 'parema alakõhu valu'."
        )
    )
    status: Literal["present", "uncertain"] = Field(
        default="present",
        description=(
            "Status of the main problem. A purely denied symptom should normally "
            "be recorded as an associated symptom of a relevant problem rather "
            "than becoming its own problem."
        ),
    )

    anatomical_site: str | None = None
    laterality: Literal["vasak", "parem", "bilateraalne"] | None = None

    quality: list[EvidenceBackedText] = Field(default_factory=list)
    course: list[EvidenceBackedText] = Field(default_factory=list)
    severity: list[EvidenceBackedText] = Field(default_factory=list)
    onset: list[EvidenceBackedText] = Field(default_factory=list)
    duration: list[EvidenceBackedText] = Field(default_factory=list)
    frequency: list[EvidenceBackedText] = Field(default_factory=list)
    provoking_factors: list[EvidenceBackedText] = Field(default_factory=list)
    relieving_factors: list[EvidenceBackedText] = Field(default_factory=list)

    negative_characteristics: list[EvidenceBackedText] = Field(
        default_factory=list,
        description=(
            "Explicitly absent characteristics of the main symptom itself, "
            "such as 'ei kiirgu' or 'öösel ei esine'."
        ),
    )

    associated_symptoms: list[AssociatedSymptom] = Field(
        default_factory=list,
        description=(
            "Other symptoms assessed in the context of this problem. "
            "These may be present, denied or uncertain."
        ),
    )

    core_evidence: list[Evidence] = Field(default_factory=list)


class SymptomExtraction(BaseModel):
    problems: list[SymptomProblem] = Field(
        default_factory=list,
        description=(
            "Distinct clinical symptom problems. Group symptom characteristics "
            "and associated positive or negative findings under the problem "
            "they were discussed in relation to."
        ),
    )


# Names of every SymptomProblem field whose value is a list[EvidenceBackedText].
# Kept in one place so evidence-walking code (see clinical/validation.py) can't
# silently miss a field when the schema grows.
EVIDENCE_BACKED_FIELDS: tuple[str, ...] = (
    "quality",
    "course",
    "severity",
    "onset",
    "duration",
    "frequency",
    "provoking_factors",
    "relieving_factors",
    "negative_characteristics",
)


class ProposedChange(BaseModel):
    """One concrete change the reviewer (Model B) proposes to the extraction."""

    kind: Literal["missing", "wrong", "misattributed"] = Field(
        description=(
            "Whether the first model MISSED this fact, stated it WRONG, or attached it "
            "to the wrong problem (MISATTRIBUTED)."
        )
    )
    problem: str = Field(
        description=(
            "The problem this relates to — an existing problem's name, or a new problem "
            "name if the whole problem was missed."
        )
    )
    field: str | None = Field(
        default=None,
        description=(
            "Which schema field it belongs in, e.g. 'severity', 'onset', "
            "'associated_symptoms', 'core_evidence', 'laterality'."
        ),
    )
    text: str = Field(
        description="The fact/characteristic in question, stated atomically."
    )
    excerpt: str | None = Field(
        default=None,
        description=(
            "Verbatim transcript excerpt supporting this. REQUIRED when kind='missing'."
        ),
    )
    reason: str = Field(description="Why the reviewer flags this change.")


class Critique(BaseModel):
    """Model B's structured review of Model A's extraction."""

    changes: list[ProposedChange] = Field(
        default_factory=list,
        description=(
            "Concrete proposed additions/corrections. Empty if A is complete and correct."
        ),
    )
    overall: str = Field(
        default="",
        description="One-line overall assessment of the first model's extraction.",
    )
