"""Tests for src.audio.chunker.OverlappingAudioChunker."""

import pytest

from src.audio.chunker import OverlappingAudioChunker


def test_rejects_non_positive_chunk_size():
    with pytest.raises(ValueError):
        OverlappingAudioChunker(chunk_size_bytes=0, step_size_bytes=1)


def test_rejects_non_positive_step_size():
    with pytest.raises(ValueError):
        OverlappingAudioChunker(chunk_size_bytes=10, step_size_bytes=0)


def test_rejects_step_larger_than_chunk():
    with pytest.raises(ValueError):
        OverlappingAudioChunker(chunk_size_bytes=10, step_size_bytes=11)


def test_no_chunk_emitted_until_buffer_is_full():
    chunker = OverlappingAudioChunker(chunk_size_bytes=10, step_size_bytes=5)
    assert chunker.add(b"1234567890"[:9]) == []


def test_emits_first_chunk_once_full():
    chunker = OverlappingAudioChunker(chunk_size_bytes=10, step_size_bytes=5)
    chunks = chunker.add(b"0123456789")
    assert chunks == [b"0123456789"]


def test_consecutive_chunks_overlap_by_step_difference():
    # chunk_size=10, step=6 -> 4 bytes of overlap between consecutive chunks
    chunker = OverlappingAudioChunker(chunk_size_bytes=10, step_size_bytes=6)
    data = bytes(range(20))  # 20 distinct byte values, easy to inspect overlap

    chunks = []
    for i in range(0, len(data), 3):
        chunks.extend(chunker.add(data[i : i + 3]))

    assert len(chunks) >= 2
    first, second = chunks[0], chunks[1]
    # Last 4 bytes of the first chunk must equal the first 4 bytes of the
    # second chunk - that's the overlap region.
    assert first[-4:] == second[:4]


def test_multiple_chunks_from_single_large_add():
    chunker = OverlappingAudioChunker(chunk_size_bytes=4, step_size_bytes=4)
    chunks = chunker.add(bytes(range(12)))  # exactly 3 non-overlapping chunks
    assert chunks == [bytes(range(0, 4)), bytes(range(4, 8)), bytes(range(8, 12))]


def test_flush_returns_remaining_partial_buffer():
    chunker = OverlappingAudioChunker(chunk_size_bytes=10, step_size_bytes=10)
    chunker.add(b"12345")
    remainder = chunker.flush()
    assert remainder == [b"12345"]


def test_flush_on_empty_buffer_returns_nothing():
    chunker = OverlappingAudioChunker(chunk_size_bytes=10, step_size_bytes=10)
    assert chunker.flush() == []


def test_flush_clears_buffer_so_it_is_not_returned_twice():
    chunker = OverlappingAudioChunker(chunk_size_bytes=10, step_size_bytes=10)
    chunker.add(b"12345")
    chunker.flush()
    assert chunker.flush() == []
