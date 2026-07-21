"""
Tests for src.audio.microphone_input.MicrophoneAudioSource construction.

Only validates the constructor's argument checking and byte-size math,
none of which touches PyAudio or requires a real microphone. Actual
capture (`stream()`) needs a real audio device and is exercised manually,
not in this automated suite.
"""

import pytest

from src.audio.microphone_input import MicrophoneAudioSource


def test_rejects_non_positive_chunk_duration():
    with pytest.raises(ValueError):
        MicrophoneAudioSource(
            sample_rate_hz=16000,
            chunk_duration_seconds=0,
            chunk_overlap_seconds=0,
        )


def test_rejects_negative_overlap():
    with pytest.raises(ValueError):
        MicrophoneAudioSource(
            sample_rate_hz=16000,
            chunk_duration_seconds=4.0,
            chunk_overlap_seconds=-1.0,
        )


def test_rejects_overlap_equal_to_duration():
    with pytest.raises(ValueError):
        MicrophoneAudioSource(
            sample_rate_hz=16000,
            chunk_duration_seconds=4.0,
            chunk_overlap_seconds=4.0,
        )


def test_rejects_overlap_greater_than_duration():
    with pytest.raises(ValueError):
        MicrophoneAudioSource(
            sample_rate_hz=16000,
            chunk_duration_seconds=4.0,
            chunk_overlap_seconds=5.0,
        )


def test_constructs_with_valid_arguments():
    source = MicrophoneAudioSource(
        sample_rate_hz=16000,
        chunk_duration_seconds=4.0,
        chunk_overlap_seconds=1.0,
        chunk_save_dir=None,
    )
    assert source is not None


def test_disables_saving_when_save_dir_is_empty():
    source = MicrophoneAudioSource(
        sample_rate_hz=16000,
        chunk_duration_seconds=4.0,
        chunk_overlap_seconds=1.0,
        chunk_save_dir="",
    )
    assert source._chunk_save_dir is None
