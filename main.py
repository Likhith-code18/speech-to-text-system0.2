"""
Entry point for the Speech-to-Text subsystem.

Wires concrete implementations into the `TranscriptionPipeline` and runs it:

    Laptop Microphone -> SpeechProvider (via factory) -> Console Display

The active Speech-to-Text provider is selected by `STT_PROVIDER` in
configuration (see config.py and src/stt/providers/factory.py).

Run with:
    python main.py
Stop with Ctrl+C.
"""

import logging
import sys

from config import config
from src.audio.microphone_input import MicrophoneAudioSource
from src.core.exceptions import AudioCaptureError, TranscriptionError
from src.core.logging_config import setup_logging
from src.display.console_display import ConsoleTranscriptDisplay
from src.pipeline.transcription_pipeline import TranscriptionPipeline
from src.stt.engine import SpeechProviderEngine
from src.stt.providers.factory import create_speech_provider

logger = logging.getLogger(__name__)


def build_pipeline(display=None) -> TranscriptionPipeline:
    """Construct the pipeline from configured, concrete components."""

    audio_source = MicrophoneAudioSource(
        sample_rate_hz=config.AUDIO_SAMPLE_RATE_HZ,
        chunk_duration_seconds=config.AUDIO_CHUNK_DURATION_SECONDS,
        chunk_overlap_seconds=config.AUDIO_CHUNK_OVERLAP_SECONDS,
        frames_per_buffer=config.AUDIO_FRAMES_PER_BUFFER,
        chunk_save_dir=config.AUDIO_CHUNK_SAVE_DIR,
    )

    speech_provider = create_speech_provider(config.STT_PROVIDER, config)
    stt_engine = SpeechProviderEngine(provider=speech_provider)

    if display is None:
        display = ConsoleTranscriptDisplay()

    return TranscriptionPipeline(
        audio_source=audio_source,
        stt_engine=stt_engine,
        display=display,
    )


def main() -> int:
    setup_logging(config.LOG_LEVEL)

    try:
        pipeline = build_pipeline()
    except (ValueError, NotImplementedError, TranscriptionError) as exc:
        logger.error("Could not initialize speech provider: %s", exc)
        return 1

    try:
        pipeline.run()
    except KeyboardInterrupt:
        logger.info("Stopped by user.")
        return 0
    except AudioCaptureError as exc:
        logger.error("Audio capture failed: %s", exc)
        return 1
    except TranscriptionError as exc:
        logger.error("Transcription failed: %s", exc)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())