"""Transcript loading.

Thin wrapper over the CSV so lessons don't repeat ``pd.read_csv`` boilerplate and
so the path is resolved relative to the repo root (works from any launch dir).
"""

import pandas as pd

from .config import TRANSCRIPTS_CSV


def load_transcripts() -> pd.DataFrame:
    """All transcripts, indexed by ``id`` (e.g. ``transcript_42``)."""
    return pd.read_csv(TRANSCRIPTS_CSV, index_col=0)


def get_transcript(transcript_id: str) -> str:
    """The transcript text for a specific id — reproducible, unlike sampling."""
    return load_transcripts().loc[transcript_id, "transcript"]


def sample_transcript(seed: int | None = None) -> str:
    """A random transcript's text. Pass ``seed`` for a repeatable pick."""
    df = load_transcripts()
    return df.sample(n=1, random_state=seed).iloc[0]["transcript"]
