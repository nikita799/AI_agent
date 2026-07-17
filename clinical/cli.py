"""Console-script helpers for the clinical package.

Registered in ``pyproject.toml`` under ``[project.scripts]``. Transcript text goes
to **stdout** and status/ids go to **stderr**, so ``random-transcript | pbcopy``
copies only the transcript (the id stays visible in the terminal).
"""

import sys


def random_transcript(argv=None) -> int:
    """Print a transcript to stdout — random, or a specific id if given.

        random-transcript                 # a random transcript
        random-transcript transcript_42   # a specific one
        random-transcript | pbcopy        # copy the text to the clipboard
    """
    argv = sys.argv[1:] if argv is None else list(argv)

    if argv and argv[0] in ("-h", "--help"):
        print(random_transcript.__doc__, file=sys.stderr)
        return 0

    from .data import get_transcript, load_transcripts

    if argv:
        tid = argv[0]
        try:
            text = get_transcript(tid)
        except KeyError:
            print(f"error: no transcript with id {tid!r}", file=sys.stderr)
            return 1
    else:
        row = load_transcripts().sample(n=1).iloc[0]
        tid, text = row.name, row["transcript"]

    print(f"picked: {tid}", file=sys.stderr)
    print(text)
    return 0
