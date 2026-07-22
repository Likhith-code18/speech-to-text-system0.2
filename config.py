"""
Centralized configuration for the Speech-to-Text subsystem.

All environment-dependent or tunable values should be read from here rather
than scattered across the codebase. Values are loaded from environment
variables (optionally via a local .env file) so that secrets such as API
keys are never hard-coded.
"""

import os

from dotenv import load_dotenv

load_dotenv()


def _env_bool(name: str, default: bool) -> bool:
    """Parse a boolean environment variable (accepts true/1/yes, case-insensitive)."""
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes")


class Config:
    """Application-wide configuration values."""

    # --- Speech-to-Text provider settings ----------------------------------
    # STT_PROVIDER selects which SpeechProvider is constructed at startup
    # (see src/stt/providers/factory.py). Each provider reads its own
    # credentials/settings below; only the active provider's fields need
    # to be set.
    STT_PROVIDER: str = os.getenv("STT_PROVIDER", "local_whisper")
    STT_LANGUAGE: str = os.getenv("STT_LANGUAGE", "en")  # ISO-639-1, e.g. "en"

    # OpenAI (src/stt/providers/openai_provider.py)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_STT_MODEL: str = os.getenv("OPENAI_STT_MODEL", "whisper-1")

    # Sarvam AI (src/stt/providers/sarvam_provider.py)
    SARVAM_API_KEY: str = os.getenv("SARVAM_API_KEY", "")
    SARVAM_STT_MODEL: str = os.getenv("SARVAM_STT_MODEL", "")

    # Local Whisper (src/stt/providers/local_whisper_provider.py) - runs
    # entirely on-device via faster-whisper; no network calls, no API key
    # (after the model is downloaded and cached on first run).
    LOCAL_WHISPER_MODEL_SIZE: str = os.getenv("LOCAL_WHISPER_MODEL_SIZE", "base")
    LOCAL_WHISPER_DEVICE: str = os.getenv("LOCAL_WHISPER_DEVICE", "cpu")
    LOCAL_WHISPER_COMPUTE_TYPE: str = os.getenv("LOCAL_WHISPER_COMPUTE_TYPE", "int8")
    # Transcription-quality parameters - see local_whisper_provider.py for
    # why each one improves accuracy on our fixed-duration audio chunks.
    LOCAL_WHISPER_BEAM_SIZE: int = int(os.getenv("LOCAL_WHISPER_BEAM_SIZE", "2"))
    LOCAL_WHISPER_VAD_FILTER: bool = _env_bool("LOCAL_WHISPER_VAD_FILTER", True)
    LOCAL_WHISPER_CONDITION_ON_PREVIOUS_TEXT: bool = _env_bool(
        "LOCAL_WHISPER_CONDITION_ON_PREVIOUS_TEXT", False
    )

    # --- Audio settings ----------------------------------------------------
    AUDIO_SAMPLE_RATE_HZ: int = int(os.getenv("AUDIO_SAMPLE_RATE_HZ", "16000"))
    AUDIO_CHUNK_DURATION_SECONDS: float = float(
        os.getenv("AUDIO_CHUNK_DURATION_SECONDS", "4.0")
    )
    AUDIO_CHUNK_OVERLAP_SECONDS: float = float(
        os.getenv("AUDIO_CHUNK_OVERLAP_SECONDS", "1.00")
    )
    AUDIO_FRAMES_PER_BUFFER: int = int(os.getenv("AUDIO_FRAMES_PER_BUFFER", "1024"))
    # Directory where each captured chunk is also saved as a .wav file, for
    # debugging/QA and as a raw audio archive. Set to "" to disable saving.
    AUDIO_CHUNK_SAVE_DIR: str = os.getenv("AUDIO_CHUNK_SAVE_DIR", "audio_chunks")

    # --- General application settings --------------------------------------
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


config = Config()