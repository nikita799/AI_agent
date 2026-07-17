"""Paths and environment loading for the clinical package.

Everything here is resolved relative to the repository root (the parent of this
package), so imports work the same no matter which directory a notebook or the
LangGraph CLI is launched from.
"""

from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
TRANSCRIPTS_CSV = DATA_DIR / "transcripts.csv"


def load_env() -> Path | None:
    """Load API keys into the environment.

    Looks for a ``.env`` at the repo root first, then falls back to the one that
    still lives in the ``assistant/`` venv directory. Returns the file that was
    loaded, or ``None`` if neither exists.
    """
    for candidate in (REPO_ROOT / ".env", REPO_ROOT / "assistant" / ".env"):
        if candidate.exists():
            load_dotenv(candidate, override=True)
            return candidate
    return None
