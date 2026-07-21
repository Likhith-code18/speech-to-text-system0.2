"""
Example: transcribe an existing audio file using the Speech-to-Text layer,
without going through the microphone pipeline.

This demonstrates that `SpeechProvider` is independently usable - useful
for batch-transcribing recordings, or for testing a provider without a
live microphone.

Usage:
    python examples/transcribe_audio_file.py path/to/recording.wav

Requires OPENAI_API_KEY to be set (e.g. in a .env file at the project
root), since this example uses the OpenAI provider by default.
"""

import logging
import sys
from pathlib import Path

# Allow running this script directly via `python examples/transcribe_audio_file.py`
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import config  # noqa: E402
from src.core.exceptions import TranscriptionError  # noqa: E402
from src.core.logging_config import setup_logging  # noqa: E402
from src.stt.providers.factory import create_speech_provider  # noqa: E402

logger = logging.getLogger(__name__)


def transcribe_file(audio_path: Path) -> str:
    """Transcribe a single audio file using the configured provider."""
    provider = create_speech_provider(config.STT_PROVIDER, config)
    audio_bytes = audio_path.read_bytes()
    return provider.transcribe(audio_bytes)


def main() -> int:
    setup_logging(config.LOG_LEVEL)

    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <path-to-audio-file>", file=sys.stderr)
        return 1

    audio_path = Path(sys.argv[1])
    if not audio_path.is_file():
        logger.error("File not found: %s", audio_path)
        return 1

    try:
        text = transcribe_file(audio_path)
    except (ValueError, NotImplementedError) as exc:
        logger.error("Could not initialize speech provider: %s", exc)
        return 1
    except TranscriptionError as exc:
        logger.error("Transcription failed: %s", exc)
        return 1

    if text:
        print(text)
    else:
        logger.info("No speech detected in %s", audio_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
