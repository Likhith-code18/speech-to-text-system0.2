"""
OpenAI implementation of `SpeechProvider`.

Wraps the OpenAI Audio Transcriptions API (`client.audio.transcriptions`)
using the official `openai` SDK. All SDK-specific exception types are
caught here and translated into `TranscriptionError`, so nothing outside
this module needs to know the `openai` package exists.
"""

import io
import logging
from sarvamai import SarvamAI


from src.core.exceptions import TranscriptionError
from src.stt.providers.base import SpeechProvider

logger = logging.getLogger(__name__)


class SarvamSpeechProvider(SpeechProvider):
    """Transcribes audio using OpenAI's Audio Transcriptions API."""

    def __init__(self, api_key: str, model: str, language: str = "") -> None:
        """
        Args:
            api_key: OpenAI API key.
            model: Transcription model name (e.g. "whisper-1",
                "gpt-4o-transcribe").
            language: Optional ISO-639-1 language code (e.g. "en") to hint
                the model with. Leave empty to let the model auto-detect.

        Raises:
            ValueError: If `api_key` or `model` is empty.
        """
        if not api_key:
            raise ValueError("SarvamSpeechProvider requires a non-empty api_key.")
        if not model:
            raise ValueError("SarvamSpeechProvider requires a non-empty model.")
        self._client = SarvamAI(api_subscription_key=api_key)
        self._model = model
        self._language = language

    def transcribe(self, audio: bytes) -> str:
        audio_file = io.BytesIO(audio)
        audio_file.name = "audio.wav"

        try:
            response = self._client.speech_to_text.transcribe(
                file=audio_file,
                model=self._model,
                mode="transcribe",
            )

        except Exception as exc:
            logger.exception(exc)
            raise TranscriptionError(
                f"Sarvam transcription request failed: {exc}"
            ) from exc


        # SDK may return either an object or a dict
        if isinstance(response, dict):
            text = response.get("transcript", "").strip()
        else:
            text = getattr(response, "transcript", "").strip()

        logger.debug("Sarvam transcription result: %r", text)
        return text
