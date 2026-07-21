"""
Abstract interfaces (contracts) for the Speech-to-Text subsystem.

Every concrete component (audio capture, transcription engine, display)
implements one of these interfaces. The pipeline in
`src/pipeline/transcription_pipeline.py` depends only on these abstractions,
never on concrete classes. This is what allows the Speech-to-Text API to be
replaced with a local model in the future without changing any other code:
a new class simply implements `SpeechToTextEngine` and is passed into the
pipeline in place of the old one.
"""

from abc import ABC, abstractmethod
from typing import Iterator

from src.core.models import Transcript


class AudioSource(ABC):
    """
    Supplies raw audio data to be transcribed.

    Concrete implementations might read from a microphone, a file, or a
    network stream. The pipeline does not care which.
    """

    @abstractmethod
    def stream(self) -> Iterator[bytes]:
        """
        Yield chunks of raw audio data as they become available.

        Returns:
            An iterator of raw audio byte chunks.
        """
        raise NotImplementedError


class SpeechToTextEngine(ABC):
    """
    Converts audio into text.

    Version 1 implements this using a cloud Speech-to-Text API. A future
    version may implement this using a local model instead. Either way,
    the rest of the system interacts only with this interface.
    """

    @abstractmethod
    def transcribe(self, audio_chunks: Iterator[bytes]) -> Iterator[Transcript]:
        """
        Transcribe a stream of audio chunks into a stream of transcripts.

        Args:
            audio_chunks: An iterator of raw audio byte chunks, typically
                produced by an `AudioSource`.

        Returns:
            An iterator of `Transcript` objects.
        """
        raise NotImplementedError


class TranscriptDisplay(ABC):
    """
    Presents transcripts to the user (console, UI overlay, etc.).
    """

    @abstractmethod
    def show(self, transcript: Transcript) -> None:
        """
        Display a single transcript.

        Args:
            transcript: The transcript to display.
        """
        raise NotImplementedError
