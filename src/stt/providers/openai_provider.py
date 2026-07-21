"""
OpenAI implementation of `SpeechProvider`.

Wraps the OpenAI Audio Transcriptions API (`client.audio.transcriptions`)
using the official `openai` SDK. All SDK-specific exception types are
caught here and translated into `TranscriptionError`, so nothing outside
this module needs to know the `openai` package exists.
"""

import io
import logging

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
    OpenAIError,
    RateLimitError,
)

from src.core.exceptions import TranscriptionError
from src.stt.providers.base import SpeechProvider

logger = logging.getLogger(__name__)


class OpenAISpeechProvider(SpeechProvider):
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
            raise ValueError("OpenAISpeechProvider requires a non-empty api_key.")
        if not model:
            raise ValueError("OpenAISpeechProvider requires a non-empty model.")

        self._client = OpenAI(api_key=api_key)
        self._model = model
        self._language = language

    def transcribe(self, audio: bytes) -> str:
        audio_file = io.BytesIO(audio)
        # The OpenAI SDK infers the audio format from the filename
        # extension, so a real file object isn't required - a named
        # in-memory buffer is enough.
        audio_file.name = "audio.wav"

        request_kwargs = {"model": self._model, "file": audio_file}
        if self._language:
            request_kwargs["language"] = self._language

        try:
            response = self._client.audio.transcriptions.create(**request_kwargs)
        except AuthenticationError as exc:
            raise TranscriptionError(
                f"OpenAI authentication failed - check OPENAI_API_KEY: {exc}"
            ) from exc
        except RateLimitError as exc:
            raise TranscriptionError(f"OpenAI rate limit exceeded: {exc}") from exc
        except (APIConnectionError, APITimeoutError) as exc:
            raise TranscriptionError(
                f"Could not reach the OpenAI API: {exc}"
            ) from exc
        except APIStatusError as exc:
            raise TranscriptionError(
                f"OpenAI API returned an error (status {exc.status_code}): {exc}"
            ) from exc
        except OpenAIError as exc:
            # Catch-all for any other SDK-level failure not covered above.
            raise TranscriptionError(f"OpenAI transcription request failed: {exc}") from exc

        text = response.text.strip()
        logger.debug("OpenAI transcription result: %r", text)
        return text
