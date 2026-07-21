"""Tests for src.audio.wav_encoding.pcm_to_wav_bytes."""

import io
import wave

from src.audio.wav_encoding import pcm_to_wav_bytes


def test_wav_header_matches_requested_parameters():
    pcm_data = bytes(range(256)) * 4  # arbitrary sample data
    wav_bytes = pcm_to_wav_bytes(
        pcm_data, channels=1, sample_width_bytes=2, sample_rate_hz=16000
    )

    with wave.open(io.BytesIO(wav_bytes), "rb") as wav_file:
        assert wav_file.getnchannels() == 1
        assert wav_file.getsampwidth() == 2
        assert wav_file.getframerate() == 16000


def test_wav_preserves_all_pcm_samples():
    pcm_data = bytes(range(256)) * 4
    wav_bytes = pcm_to_wav_bytes(
        pcm_data, channels=1, sample_width_bytes=2, sample_rate_hz=16000
    )

    with wave.open(io.BytesIO(wav_bytes), "rb") as wav_file:
        assert wav_file.readframes(wav_file.getnframes()) == pcm_data


def test_stereo_encoding():
    pcm_data = bytes(range(256)) * 4
    wav_bytes = pcm_to_wav_bytes(
        pcm_data, channels=2, sample_width_bytes=2, sample_rate_hz=8000
    )

    with wave.open(io.BytesIO(wav_bytes), "rb") as wav_file:
        assert wav_file.getnchannels() == 2
        assert wav_file.getframerate() == 8000
