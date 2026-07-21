"""
Provider-agnostic `SpeechToTextEngine`.

Adapts any `SpeechProvider` (see `src/stt/providers/base.py`) into the
`SpeechToTextEngine` interface that `TranscriptionPipeline` depends on.
This class contains no provider-specific logic whatsoever - it just loops
over incoming audio chunks and delegates each one to the injected
provider. Swapping OpenAI for Deepgram, Google Speech, or a local Whisper
model never touches this file; only which `SpeechProvider` is constructed
in `main.py` changes.
"""

import logging
from typing import Iterator

from src.core.interfaces import SpeechToTextEngine
from src.core.models import Transcript
from src.stt.providers.base import SpeechProvider

logger = logging.getLogger(__name__)


class SpeechProviderEngine(SpeechToTextEngine):
    """`SpeechToTextEngine` backed by an injected `SpeechProvider`."""

    def __init__(self, provider: SpeechProvider) -> None:
        self._provider = provider

    def transcribe(self, audio_chunks: Iterator[bytes]) -> Iterator[Transcript]:
        """
        Transcribe each audio chunk via the configured provider.

        Chunks the provider recognizes no speech in (empty result) are
        skipped rather than yielded as empty transcripts.

        Raises:
            TranscriptionError: Propagated from the underlying
                `SpeechProvider` if a request fails.
        """
        for chunk in audio_chunks:
            text = self._provider.transcribe(chunk)
            if not text:
                logger.debug("No speech recognized in this chunk; skipping.")
                continue
            yield Transcript(text=text, is_final=True)
