"""
Transcription pipeline: orchestrates audio capture, transcription, and
display.

This module depends only on the abstract interfaces in
`src.core.interfaces`. It has no knowledge of microphones, specific APIs,
or local models - those details live entirely in the concrete classes that
are injected into it. Replacing the Speech-to-Text API with a local model
means constructing a different `SpeechToTextEngine` implementation and
passing it in here; this file does not change.
"""

import logging

from src.core.interfaces import AudioSource, SpeechToTextEngine, TranscriptDisplay

logger = logging.getLogger(__name__)


class TranscriptionPipeline:
    """Coordinates the audio -> transcription -> display flow."""

    def __init__(
        self,
        audio_source: AudioSource,
        stt_engine: SpeechToTextEngine,
        display: TranscriptDisplay,
    ) -> None:
        self._audio_source = audio_source
        self._stt_engine = stt_engine
        self._display = display

    def run(self) -> None:
        """Run the pipeline until the audio source is exhausted."""
        logger.info("Starting transcription pipeline.")
        audio_chunks = self._audio_source.stream()
        transcripts = self._stt_engine.transcribe(audio_chunks)
        for transcript in transcripts:
            self._display.show(transcript)
