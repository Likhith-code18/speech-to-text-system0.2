import threading

from src.core.interfaces import TranscriptDisplay
from src.core.models import Transcript


class StreamlitTranscriptDisplay(TranscriptDisplay):
    """
    Thread-safe TranscriptDisplay implementation for Streamlit.
    Stores the latest transcript in memory so the Streamlit UI can display it.
    """

    def __init__(self):
        self._final_text = ""
        self._partial_text = ""
        self._lock = threading.Lock()

    def show(self, transcript: Transcript) -> None:
        with self._lock:
            if not transcript.text.strip():
                return

            if transcript.is_final:
                self._final_text += transcript.text + " "
                self._partial_text = ""
            else:
                self._partial_text = transcript.text

    def get_transcript(self) -> str:
        with self._lock:
            return (self._final_text + self._partial_text).strip()

    def clear(self) -> None:
        with self._lock:
            self._final_text = ""
            self._partial_text = ""