"""
Raw PCM -> WAV encoding.

Separated from `microphone_input.py` so it can be unit tested with plain
bytes, independent of any audio hardware.
"""

import io
import wave


def pcm_to_wav_bytes(
    pcm_data: bytes, channels: int, sample_width_bytes: int, sample_rate_hz: int
) -> bytes:
    """
    Wrap raw PCM samples in a self-contained WAV container.

    WAV is used (rather than passing raw PCM around) because it embeds its
    own sample rate, channel count, and bit depth, so downstream consumers
    (any `SpeechProvider`) never need those parameters passed out of band,
    and the file plays correctly in any standard audio player.

    Args:
        pcm_data: Raw, headerless PCM audio samples.
        channels: Number of audio channels (1 = mono).
        sample_width_bytes: Bytes per sample (2 for 16-bit PCM).
        sample_rate_hz: Sample rate in Hz.

    Returns:
        Bytes of a complete WAV file.
    """
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width_bytes)
        wav_file.setframerate(sample_rate_hz)
        wav_file.writeframes(pcm_data)
    return buffer.getvalue()
