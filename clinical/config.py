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
    """Load API keys from the repo-root ``.env`` into the environment.

    Returns the file that was loaded, or ``None`` if it doesn't exist.
    """
    env_file = REPO_ROOT / ".env"
    if env_file.exists():
        load_dotenv(env_file, override=True)
        return env_file
    return None
