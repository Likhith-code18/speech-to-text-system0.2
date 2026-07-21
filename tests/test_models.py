"""Tests for src.core.models."""

from src.core.models import Transcript


def test_transcript_defaults_to_final():
    transcript = Transcript(text="hello world")
    assert transcript.is_final is True
    assert transcript.text == "hello world"
    assert transcript.timestamp is not None


def test_transcript_can_be_interim():
    transcript = Transcript(text="hel", is_final=False)
    assert transcript.is_final is False
