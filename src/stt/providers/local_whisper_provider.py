"""
Local Whisper implementation of `SpeechProvider`, using faster-whisper.

Runs transcription entirely on-device (CPU or GPU) - no network calls, no
API key. The model is loaded once, at construction time, and reused for
every `transcribe()` call; loading it per-chunk would be far too slow to
be usable.
"""

import io
import logging

from faster_whisper import WhisperModel

from src.core.exceptions import TranscriptionError
from src.stt.providers.base import SpeechProvider

logger = logging.getLogger(__name__)


class LocalWhisperSpeechProvider(SpeechProvider):
    """Transcribes audio locally using faster-whisper (no network/API key)."""

    def __init__(
        self,
        model_size: str,
        device: str,
        compute_type: str,
        language: str = "",
        beam_size: int = 5,
        vad_filter: bool = True,
        condition_on_previous_text: bool = False,
    ) -> None:
        """
        Args:
            model_size: Whisper model size/name (e.g. "tiny", "base",
                "small", "medium", "large-v3"). Larger models are more
                accurate but slower and use more memory. The model is
                downloaded from Hugging Face on first use and cached
                locally afterward - the first run needs internet access,
                later runs do not.
            device: "cpu" or "cuda".
            compute_type: CTranslate2 quantization, e.g. "int8" (fastest
                on CPU), "float16" (typical for GPU), "float32".
            language: ISO-639-1 language code to force (e.g. "en"). Leave
                empty to let Whisper auto-detect the spoken language.
            beam_size: Beam search width. Whisper explores this many
                candidate transcriptions in parallel at each step and
                keeps the most probable one, instead of greedily
                committing to the single best token at every step.
                Higher values (5-10) catch fewer local mistakes, i.e.
                a word that sounded plausible token-by-token but was
                wrong in context, at the cost of more compute per chunk.
            vad_filter: Whether to run Voice Activity Detection before
                transcribing. Our audio chunks are fixed-duration slices
                of a continuous recording (see `microphone_input.py`),
                so a chunk very often starts or ends mid-silence, or is
                pure silence/background noise. Whisper is well documented
                to hallucinate plausible-sounding text (repeated phrases,
                stock captioning lines) when fed silence or noise. VAD
                filtering detects and skips those non-speech regions
                before decoding, which is one of the single biggest
                accuracy wins for exactly this chunked-audio setup.
            condition_on_previous_text: Whether Whisper conditions each
                segment's decoding on the text of previous segments
                *within the same transcribe() call*. Left at faster-whisper's
                default (True), this is a well-documented trigger for
                repetition-loop hallucination on short or silence-heavy
                audio, since the model over-anchors on its own prior
                output. Because each chunk here is transcribed
                independently anyway (no context is shared across chunks
                regardless of this setting), there is no accuracy benefit
                to keeping it on for our use case - only the repetition
                risk. Defaulting it to False removes that failure mode.

        Raises:
            TranscriptionError: If the model fails to load (e.g. invalid
                model name, no internet on first run, unsupported device).
        """
        self._language = language or None
        self._beam_size = beam_size
        self._vad_filter = vad_filter
        self._condition_on_previous_text = condition_on_previous_text

        try:
            self._model = WhisperModel(
                model_size, device=device, compute_type=compute_type
            )
        except Exception as exc:
            raise TranscriptionError(
                f"Failed to load local Whisper model '{model_size}': {exc}"
            ) from exc

    def transcribe(self, audio: bytes) -> str:
        audio_file = io.BytesIO(audio)
        try:
            segments, _info = self._model.transcribe(
                audio_file,
                language=self._language,
                beam_size=self._beam_size,
                vad_filter=self._vad_filter,
                condition_on_previous_text=self._condition_on_previous_text,
            )
            text = " ".join(segment.text.strip() for segment in segments).strip()
        except Exception as exc:
            raise TranscriptionError(
                f"Local Whisper transcription failed: {exc}"
            ) from exc

        logger.debug("Local Whisper transcription result: %r", text)
        return text