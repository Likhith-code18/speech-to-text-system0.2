"""
Abstract interface for a Speech-to-Text provider.

A `SpeechProvider` wraps exactly one external speech recognition backend -
a cloud API or a local model - behind a single operation: take a complete
audio clip, return the recognized text. It has no knowledge of microphones,
audio streaming, or how results get displayed; those concerns belong to
`AudioSource`, `SpeechToTextEngine`, and `TranscriptDisplay` in
`src/core/interfaces.py`.

This narrow contract is what makes providers interchangeable. Every
provider - `OpenAISpeechProvider` today; Deepgram, Google Speech-to-Text,
or a local Whisper model in the future - implements only `transcribe()`.
`src/stt/engine.py` adapts any `SpeechProvider` into the pipeline-facing
`SpeechToTextEngine` interface, so adding a provider never requires
touching the pipeline, audio capture, or display code.
"""

from abc import ABC, abstractmethod


class SpeechProvider(ABC):
    """Transcribes a single, complete audio clip using one STT backend."""

    @abstractmethod
    def transcribe(self, audio: bytes) -> str:
        """
        Transcribe a complete, self-contained audio clip.

        Args:
            audio: Raw bytes of a self-contained audio file (e.g. WAV).
                The clip is expected to contain a single utterance or a
                short recording; providers are not required to support
                arbitrarily long inputs.

        Returns:
            The recognized text. An empty string means the provider ran
            successfully but detected no speech - this is not an error.

        Raises:
            TranscriptionError: If the provider fails to produce a result
                (e.g. authentication failure, network error, rate limit,
                malformed audio, or any other backend-specific failure).
                Implementations must not let backend-specific exception
                types escape this method.
        """
        raise NotImplementedError
