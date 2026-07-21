"""Tests for src.stt.providers.openai_provider.OpenAISpeechProvider."""

import pytest

from src.stt.providers.openai_provider import OpenAISpeechProvider


def test_requires_api_key():
    with pytest.raises(ValueError):
        OpenAISpeechProvider(api_key="", model="whisper-1")


def test_requires_model():
    with pytest.raises(ValueError):
        OpenAISpeechProvider(api_key="test-key", model="")


def test_constructs_with_valid_arguments():
    provider = OpenAISpeechProvider(api_key="test-key", model="whisper-1")
    assert provider is not None
