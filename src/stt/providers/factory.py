"""
Factory for constructing a `SpeechProvider` from configuration.

This is the single place in the codebase that maps a provider name to a
concrete `SpeechProvider` implementation. Adding a new provider means:

    1. Implement a new `SpeechProvider` subclass under `src/stt/providers/`.
    2. Add its config fields to `config.py`.
    3. Add one branch here.

No other file changes - `SpeechProviderEngine`, `TranscriptionPipeline`,
and `main.py` all depend only on the `SpeechProvider` interface.
"""

from config import Config
from src.stt.providers.base import SpeechProvider
from src.stt.providers.local_whisper_provider import LocalWhisperSpeechProvider
from src.stt.providers.openai_provider import OpenAISpeechProvider

# Providers that are planned but not yet implemented. Kept as an explicit
# set (rather than falling into a generic "unknown provider" error) so the
# error message correctly distinguishes "not built yet" from "typo/never
# heard of it".
_PLANNED_PROVIDERS = {"deepgram", "google"}


def create_speech_provider(provider_name: str, config: Config) -> SpeechProvider:
    """
    Construct the `SpeechProvider` identified by `provider_name`.

    Args:
        provider_name: Case-insensitive provider identifier, e.g. "openai".
        config: Application configuration to read provider credentials/
            settings from.

    Returns:
        A configured `SpeechProvider` instance.

    Raises:
        ValueError: If `provider_name` is empty, unrecognized, or if
            required configuration for that provider is missing.
        NotImplementedError: If `provider_name` names a provider that is
            planned but not yet implemented (Deepgram, Google).
    """
    if not provider_name:
        raise ValueError("provider_name must not be empty.")

    normalized = provider_name.strip().lower()

    if normalized == "openai":
        if not config.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY must be set to use the 'openai' speech provider."
            )
        return OpenAISpeechProvider(
            api_key=config.OPENAI_API_KEY,
            model=config.OPENAI_STT_MODEL,
            language=config.STT_LANGUAGE,
        )

    if normalized == "local_whisper":
        return LocalWhisperSpeechProvider(
            model_size=config.LOCAL_WHISPER_MODEL_SIZE,
            device=config.LOCAL_WHISPER_DEVICE,
            compute_type=config.LOCAL_WHISPER_COMPUTE_TYPE,
            language=config.STT_LANGUAGE,
            beam_size=config.LOCAL_WHISPER_BEAM_SIZE,
            vad_filter=config.LOCAL_WHISPER_VAD_FILTER,
            condition_on_previous_text=config.LOCAL_WHISPER_CONDITION_ON_PREVIOUS_TEXT,
        )

    if normalized in _PLANNED_PROVIDERS:
        raise NotImplementedError(
            f"The '{normalized}' speech provider is planned but not yet "
            "implemented. Implement a SpeechProvider subclass under "
            "src/stt/providers/ and register it in create_speech_provider()."
        )

    raise ValueError(f"Unknown speech provider: {provider_name!r}")