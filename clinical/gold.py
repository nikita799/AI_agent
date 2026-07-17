"""Phase 2 — apply accepted reviewer proposals and save a gold record.

Deterministic, LLM-free: given the human's accepted `ProposedChange`s, merge them into a copy
of the extraction (best-effort, per field), then persist a `GoldRecord` with full provenance
(both models, the critique, the human decisions). Gold records contain transcript excerpts, so
they live under a gitignored `gold/` directory.
"""

from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, Field

from .config import REPO_ROOT
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

_LATERALITY = {"vasak", "parem", "bilateraalne"}


class GoldRecord(BaseModel):
    """A signed-off, dual-checked extraction plus its provenance."""

    transcript_id: str
    encounter_date: str | None = None
    extractor_model: str
    reviewer_model: str
    extraction: SymptomExtraction  # the FINAL (merged) extraction
    critique: Critique  # the reviewer's full critique
    decisions: list[dict] = Field(default_factory=list)  # per-proposal: accepted + apply note
    created_at: str
    status: str = "gold"


def _find_problem(extraction: SymptomExtraction, name: str) -> SymptomProblem | None:
    target = (name or "").strip().lower()
    for problem in extraction.problems:
        if problem.problem.strip().lower() == target:
            return problem
    return None


def _apply_one(extraction: SymptomExtraction, change: ProposedChange) -> tuple[bool, str]:
    """Best-effort merge of one accepted change. Returns (applied, human-readable note)."""
    problem = _find_problem(extraction, change.problem)
    if problem is None:
        problem = SymptomProblem(problem=change.problem or "tundmatu probleem")
        extraction.problems.append(problem)

    field = (change.field or "").strip().lower()
    evidence = [Evidence(speaker="unknown", excerpt=change.excerpt)] if change.excerpt else []

    if field in EVIDENCE_BACKED_FIELDS:
        if not evidence:
            return False, f"'{field}' needs a supporting excerpt; none provided"
        getattr(problem, field).append(EvidenceBackedText(text=change.text, evidence=evidence))
        return True, f"added to {field}"
    if field == "core_evidence":
        if not evidence:
            return False, "core_evidence needs an excerpt"
        problem.core_evidence.extend(evidence)
        return True, "added core_evidence"
    if field == "associated_symptoms":
        problem.associated_symptoms.append(
            AssociatedSymptom(symptom=change.text, status="present", evidence=evidence)
        )
        return True, "added associated_symptom"
    if field == "laterality":
        if change.text in _LATERALITY:
            problem.laterality = change.text
            return True, "set laterality"
        return False, f"laterality '{change.text}' is not one of {sorted(_LATERALITY)}"
    if field in ("anatomical_site", "anatomical site"):
        problem.anatomical_site = change.text
        return True, "set anatomical_site"

    # 'wrong' / 'misattributed' / unknown field — recorded, but left for the human (or Phase 3).
    return False, f"not auto-applied (field='{field}', kind='{change.kind}')"


def apply_accepted(
    extraction: SymptomExtraction, accepted: list[ProposedChange]
) -> tuple[SymptomExtraction, list[dict]]:
    """Return a merged COPY of the extraction plus a note per accepted change.

    The original extraction is not mutated (preserved for provenance).
    """
    merged = extraction.model_copy(deep=True)
    notes = []
    for change in accepted:
        applied, note = _apply_one(merged, change)
        notes.append(
            {
                "kind": change.kind,
                "problem": change.problem,
                "field": change.field,
                "text": change.text,
                "applied": applied,
                "note": note,
            }
        )
    return merged, notes


def build_gold_record(
    transcript_id: str,
    extraction: SymptomExtraction,
    critique: Critique,
    decisions: list[dict],
    extractor_model: str,
    reviewer_model: str,
    encounter_date: str | None = None,
) -> GoldRecord:
    """Assemble a GoldRecord (stamps created_at in UTC)."""
    return GoldRecord(
        transcript_id=transcript_id,
        encounter_date=encounter_date,
        extractor_model=extractor_model,
        reviewer_model=reviewer_model,
        extraction=extraction,
        critique=critique,
        decisions=decisions,
        created_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )


def _gold_dir(gold_dir=None) -> Path:
    return Path(gold_dir) if gold_dir else (REPO_ROOT / "gold")


def save_gold(record: GoldRecord, gold_dir=None) -> Path:
    """Write the record to gold/<transcript_id>.json (creating gold/ if needed)."""
    directory = _gold_dir(gold_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{record.transcript_id}.json"
    path.write_text(record.model_dump_json(indent=2))
    return path


def load_gold(transcript_id: str, gold_dir=None) -> GoldRecord | None:
    """Load a gold record, or None if this transcript hasn't been curated yet."""
    path = _gold_dir(gold_dir) / f"{transcript_id}.json"
    if not path.exists():
        return None
    return GoldRecord.model_validate_json(path.read_text())


def gold_progress(gold_dir=None) -> list[str]:
    """Transcript ids that have a saved gold record, sorted."""
    directory = _gold_dir(gold_dir)
    if not directory.exists():
        return []
    return sorted(path.stem for path in directory.glob("*.json"))
