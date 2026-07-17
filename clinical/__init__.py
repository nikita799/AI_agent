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
from .models import DEFAULT_MODEL, get_chat_model, get_extraction_model
from .prompts import (
    EXTRACTION_SYSTEM_PROMPT,
    build_extraction_user_message,
    build_repair_message,
)
from .render import show_symptom_evidence_matrix
from .schema import (
    EVIDENCE_BACKED_FIELDS,
    AssociatedSymptom,
    Evidence,
    EvidenceBackedText,
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
    "Evidence",
    "EvidenceBackedText",
    "AssociatedSymptom",
    "SymptomProblem",
    "SymptomExtraction",
    "EVIDENCE_BACKED_FIELDS",
    "find_unsupported_excerpts",
    "iter_evidence",
    "normalize",
]
