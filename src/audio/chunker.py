"""
Fixed-size, overlapping sliding-window chunker for a raw PCM byte stream.

This class has no dependency on PyAudio, threads, or any I/O - it just
turns "bytes arriving over time" into "fixed-size overlapping byte
windows". That separation is what makes it possible to unit test the
windowing math deterministically, without a real microphone or audio
device.

Why overlapping windows: without overlap, a word spoken exactly across a
chunk boundary gets split between two independent transcription requests
and is often garbled or dropped by the Speech-to-Text API in *both*
chunks. Overlap guarantees that boundary audio appears whole in at least
one chunk.
"""

from typing import List


class OverlappingAudioChunker:
    """Buffers raw PCM bytes and emits fixed-size, overlapping windows."""

    def __init__(self, chunk_size_bytes: int, step_size_bytes: int) -> None:
        """
        Args:
            chunk_size_bytes: Size of each emitted window, in bytes.
            step_size_bytes: How far the window advances between chunks,
                in bytes. Must be less than `chunk_size_bytes` for the
                windows to overlap (equal to it means no overlap).

        Raises:
            ValueError: If the sizes are non-positive, or if
                `step_size_bytes` exceeds `chunk_size_bytes` (which would
                silently skip audio instead of overlapping it).
        """
        if chunk_size_bytes <= 0:
            raise ValueError("chunk_size_bytes must be positive.")
        if step_size_bytes <= 0:
            raise ValueError("step_size_bytes must be positive.")
        if step_size_bytes > chunk_size_bytes:
            raise ValueError(
                "step_size_bytes must not exceed chunk_size_bytes, or audio "
                "would be skipped between chunks instead of overlapped."
            )

        self._chunk_size_bytes = chunk_size_bytes
        self._step_size_bytes = step_size_bytes
        self._buffer = bytearray()

    def add(self, data: bytes) -> List[bytes]:
        """
        Append newly captured PCM bytes and return any windows that are
        now complete.

        Args:
            data: Newly captured raw PCM bytes.

        Returns:
            Zero or more complete, fixed-size byte windows, in capture
            order. Usually zero or one; more than one only if `data` was
            large enough to complete several windows at once.
        """
        self._buffer.extend(data)

        chunks: List[bytes] = []
        while len(self._buffer) >= self._chunk_size_bytes:
            chunks.append(bytes(self._buffer[: self._chunk_size_bytes]))
            del self._buffer[: self._step_size_bytes]
        return chunks

    def flush(self) -> List[bytes]:
        """
        Return whatever partial audio remains buffered, as a final
        (possibly shorter than `chunk_size_bytes`) window.

        Call this once, after capture has stopped, so the last few
        seconds of speech - which may never reach a full window - aren't
        silently discarded.
        """
        if not self._buffer:
            return []
        remainder = bytes(self._buffer)
        self._buffer.clear()
        return [remainder]
