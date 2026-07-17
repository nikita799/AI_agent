"""Stable, LangGraph-free core for the clinical symptom-extraction lessons.

Import what you need and build your graph on top:

    from clinical import get_extraction_model, EXTRACTION_SYSTEM_PROMPT
    from clinical import load_transcripts, show_symptom_evidence_matrix

Importing the package loads API keys from ``.env`` automatically.
"""

import warnings as _warnings

# Silence the benign langchain/pydantic-v1 shim warning on Python 3.14 — our schema
# is Pydantic v2 and structured output is unaffected. Targeted so real warnings show.
_warnings.filterwarnings(
    "ignore",
    message=r"Core Pydantic V1 functionality isn't compatible with Python 3\.14.*",
)

from .config import DATA_DIR, REPO_ROOT, TRANSCRIPTS_CSV, load_env
from .data import get_transcript, load_transcripts, sample_transcript
from .models import (
    DEFAULT_MODEL,
    REVIEWER_MODEL,
    get_chat_model,
    get_extraction_model,
    get_reviewer_model,
)
from .prompts import (
    EXTRACTION_SYSTEM_PROMPT,
    REVIEW_SYSTEM_PROMPT,
    build_extraction_user_message,
    build_repair_message,
    build_review_user_message,
)
from .gold import (
    GoldRecord,
    apply_accepted,
    build_gold_record,
    gold_progress,
    load_gold,
    save_gold,
)
from .render import (
    show_review_diff,
    show_symptom_evidence_matrix,
    show_transcript_coverage,
)
from .schema import (
    EVIDENCE_BACKED_FIELDS,
    AssociatedSymptom,
    Critique,
    Evidence,
    EvidenceBackedText,
    ProposedChange,
    SymptomExtraction,
    SymptomProblem,
)
from .validation import find_unsupported_excerpts, iter_evidence, normalize

# Load API keys as a side effect of importing the package.
load_env()

__all__ = [
    "REPO_ROOT",
    "DATA_DIR",
    "TRANSCRIPTS_CSV",
    "load_env",
    "load_transcripts",
    "get_transcript",
    "sample_transcript",
    "DEFAULT_MODEL",
    "get_chat_model",
    "get_extraction_model",
    "EXTRACTION_SYSTEM_PROMPT",
    "build_extraction_user_message",
    "build_repair_message",
    "show_symptom_evidence_matrix",
    "show_transcript_coverage",
    "show_review_diff",
    "Evidence",
    "EvidenceBackedText",
    "AssociatedSymptom",
    "SymptomProblem",
    "SymptomExtraction",
    "EVIDENCE_BACKED_FIELDS",
    "find_unsupported_excerpts",
    "iter_evidence",
    "normalize",
    "Critique",
    "ProposedChange",
    "REVIEWER_MODEL",
    "get_reviewer_model",
    "REVIEW_SYSTEM_PROMPT",
    "build_review_user_message",
    "GoldRecord",
    "apply_accepted",
    "build_gold_record",
    "save_gold",
    "load_gold",
    "gold_progress",
]
