"""
Console implementation of `TranscriptDisplay`.

Displaying a transcript is simple and not dependent on the microphone or
API work, so it is implemented here to keep the pipeline runnable
end-to-end once the other components are in place.
"""

from src.core.interfaces import TranscriptDisplay
from src.core.models import Transcript


class ConsoleTranscriptDisplay(TranscriptDisplay):
    """Prints transcripts to standard output."""

    def show(self, transcript: Transcript) -> None:
        marker = "FINAL" if transcript.is_final else "..."
        print(f"[{transcript.timestamp:%H:%M:%S}] ({marker}) {transcript.text}")
