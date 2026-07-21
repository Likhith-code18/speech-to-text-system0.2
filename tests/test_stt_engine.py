"""Tests for src.stt.engine.SpeechProviderEngine."""

from src.stt.engine import SpeechProviderEngine
from src.stt.providers.base import SpeechProvider


class FakeSpeechProvider(SpeechProvider):
    """A SpeechProvider that returns pre-set results without any API calls."""

    def __init__(self, results):
        self._results = iter(results)

    def transcribe(self, audio: bytes) -> str:
        return next(self._results)


def test_engine_yields_transcript_per_nonempty_result():
    provider = FakeSpeechProvider(["hello world", "goodbye"])
    engine = SpeechProviderEngine(provider)

    transcripts = list(engine.transcribe(iter([b"chunk1", b"chunk2"])))

    assert [t.text for t in transcripts] == ["hello world", "goodbye"]
    assert all(t.is_final for t in transcripts)


def test_engine_skips_empty_results():
    provider = FakeSpeechProvider(["", "hello"])
    engine = SpeechProviderEngine(provider)

    transcripts = list(engine.transcribe(iter([b"silence", b"chunk"])))

    assert [t.text for t in transcripts] == ["hello"]


def test_engine_handles_no_chunks():
    provider = FakeSpeechProvider([])
    engine = SpeechProviderEngine(provider)

    transcripts = list(engine.transcribe(iter([])))

    assert transcripts == []
