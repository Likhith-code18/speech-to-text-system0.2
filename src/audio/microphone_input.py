"""
Microphone-based implementation of `AudioSource`.

Captures audio continuously from the laptop's default input device using
PyAudio directly, and emits fixed-duration, overlapping WAV chunks.

Design notes (why this replaces a `speech_recognition`-based approach):

1. Capture runs on a background thread via PyAudio's callback API,
   completely decoupled from how fast the chunk is consumed downstream.
   A previous phrase-based design (`recognizer.listen()` in a generator)
   paused capture entirely while a chunk was sent to the Speech-to-Text
   API and transcribed - anything spoken during that network round-trip
   was silently lost. Here, PortAudio keeps filling an internal queue
   regardless of what the consumer is doing, so no audio is dropped while
   waiting on the API.

2. Chunking is time-based and fixed-size, not silence/energy-threshold
   based. An energy threshold can misclassify quiet speech as silence and
   drop it entirely; fixed-duration windows capture everything regardless
   of volume.

3. Consecutive chunks overlap (see `OverlappingAudioChunker`). Without
   overlap, a word spoken exactly on a chunk boundary is split across two
   independent transcription requests and often garbled or dropped in
   both. Overlap guarantees boundary audio appears whole in at least one
   chunk. The trade-off: the overlapping region's words will appear in
   both chunks' transcripts; de-duplicating that text is a display/engine
   concern, not this module's (see README "Known Limitations").
"""

import logging
import queue
from datetime import datetime
from pathlib import Path
from typing import Iterator, Optional

import pyaudio

from src.audio.chunker import OverlappingAudioChunker
from src.audio.wav_encoding import pcm_to_wav_bytes
from src.core.exceptions import AudioCaptureError
from src.core.interfaces import AudioSource

logger = logging.getLogger(__name__)

# 16-bit PCM is the standard, widely-supported format for speech capture
# and is what every major Speech-to-Text API expects.
_SAMPLE_FORMAT = pyaudio.paInt16
_SAMPLE_WIDTH_BYTES = 2
_CHANNELS = 1

# If the internal frame queue backs up beyond this many pending frames, it
# means the consumer (transcription) is falling behind real-time capture.
# Audio is still never dropped (the queue is unbounded so the audio
# callback never blocks) - this is purely a diagnostic signal.
_QUEUE_BACKLOG_WARNING_THRESHOLD = 100


class MicrophoneAudioSource(AudioSource):
    """
    Captures audio from the laptop microphone as overlapping WAV chunks.

    Each chunk is also written to disk as a standalone `.wav` file (if
    `chunk_save_dir` is set), which is useful both for debugging
    transcription quality and as a raw audio archive of the session.
    """

    def __init__(
        self,
        sample_rate_hz: int,
        chunk_duration_seconds: float,
        chunk_overlap_seconds: float,
        frames_per_buffer: int = 1024,
        chunk_save_dir: Optional[str] = None,
    ) -> None:
        """
        Args:
            sample_rate_hz: Capture sample rate, in Hz.
            chunk_duration_seconds: Length of each emitted audio chunk.
            chunk_overlap_seconds: How much consecutive chunks overlap.
                Must be strictly less than `chunk_duration_seconds`.
            frames_per_buffer: PyAudio's internal callback buffer size, in
                frames. Smaller values reduce latency and buffering delay
                at a small CPU-overhead cost; 1024 is a safe default at
                16 kHz.
            chunk_save_dir: Directory to save each chunk as a `.wav` file.
                Pass `None` (or an empty string) to disable saving to
                disk entirely.

        Raises:
            ValueError: If `chunk_overlap_seconds` is not strictly less
                than `chunk_duration_seconds`, or either is non-positive.
        """
        if chunk_duration_seconds <= 0:
            raise ValueError("chunk_duration_seconds must be positive.")
        if chunk_overlap_seconds < 0:
            raise ValueError("chunk_overlap_seconds must not be negative.")
        if chunk_overlap_seconds >= chunk_duration_seconds:
            raise ValueError(
                "chunk_overlap_seconds must be strictly less than "
                "chunk_duration_seconds."
            )

        self._sample_rate_hz = sample_rate_hz
        self._chunk_duration_seconds = chunk_duration_seconds
        self._chunk_overlap_seconds = chunk_overlap_seconds
        self._frames_per_buffer = frames_per_buffer

        self._chunk_save_dir = self._prepare_save_dir(chunk_save_dir)

        chunk_size_bytes = self._seconds_to_bytes(chunk_duration_seconds)
        step_size_bytes = chunk_size_bytes - self._seconds_to_bytes(
            chunk_overlap_seconds
        )
        self._chunker = OverlappingAudioChunker(chunk_size_bytes, step_size_bytes)

        self._frame_queue: "queue.Queue[bytes]" = queue.Queue()
        self._running = True

    def _seconds_to_bytes(self, seconds: float) -> int:
        frames = int(seconds * self._sample_rate_hz)
        return frames * _SAMPLE_WIDTH_BYTES * _CHANNELS

    @staticmethod
    def _prepare_save_dir(chunk_save_dir: Optional[str]) -> Optional[Path]:
        if not chunk_save_dir:
            return None
        path = Path(chunk_save_dir)
        try:
            path.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            logger.warning(
                "Could not create audio chunk directory %s (%s); "
                "chunks will not be saved to disk.",
                path,
                exc,
            )
            return None
        return path

    def _audio_callback(self, in_data, frame_count, time_info, status_flags):
        # Runs on PortAudio's own thread. Must return quickly and must
        # never block, or audio will underrun/glitch.
        if status_flags:
            logger.warning("PyAudio reported an input status flag: %s", status_flags)

        self._frame_queue.put_nowait(in_data)

        backlog = self._frame_queue.qsize()
        if backlog > _QUEUE_BACKLOG_WARNING_THRESHOLD:
            logger.warning(
                "Audio frame queue backlog is %d frames - transcription is "
                "falling behind real-time capture. No audio is being "
                "dropped, but latency will grow.",
                backlog,
            )

        return (None, pyaudio.paContinue)

    def stream(self) -> Iterator[bytes]:
        """
        Yield fixed-duration, overlapping WAV-encoded audio chunks.

        Runs indefinitely until the caller stops iterating (e.g. on
        `KeyboardInterrupt`) or an unrecoverable audio device error occurs.
        Capture continues in the background regardless of how long each
        chunk takes to be transcribed downstream.

        Raises:
            AudioCaptureError: If the microphone cannot be opened, or a
                device-level error occurs during capture.
        """
        pyaudio_instance = pyaudio.PyAudio()

        try:
            stream = pyaudio_instance.open(
                format=_SAMPLE_FORMAT,
                channels=_CHANNELS,
                rate=self._sample_rate_hz,
                input=True,
                frames_per_buffer=self._frames_per_buffer,
                stream_callback=self._audio_callback,
            )
        except OSError as exc:
            pyaudio_instance.terminate()
            raise AudioCaptureError(f"Unable to open microphone stream: {exc}") from exc

        chunk_index = 0

        try:
            stream.start_stream()
            logger.info(
                "Listening (chunk=%.1fs, overlap=%.1fs). Press Ctrl+C to stop.",
                self._chunk_duration_seconds,
                self._chunk_overlap_seconds,
            )

            while self._running:
                try:
                    frame = self._frame_queue.get(timeout=0.5)
                except queue.Empty:
                    if not stream.is_active():
                        raise AudioCaptureError(
                            "Microphone stream stopped unexpectedly."
                        )
                    continue

                for pcm_chunk in self._chunker.add(frame):
                    yield self._finalize_chunk(pcm_chunk, chunk_index)
                    chunk_index += 1

        except KeyboardInterrupt:
            # On the way out, don't discard the last partial window - it
            # may hold several seconds of unspoken/uncaptured speech.
            for pcm_chunk in self._chunker.flush():
                yield self._finalize_chunk(pcm_chunk, chunk_index)
                chunk_index += 1
            raise
        except AudioCaptureError:
            raise
        except Exception as exc:
            raise AudioCaptureError(f"Microphone capture failed: {exc}") from exc
        finally:
            self._close_stream(stream, pyaudio_instance)

    def _finalize_chunk(self, pcm_chunk: bytes, chunk_index: int) -> bytes:
        """Encode a raw PCM chunk as WAV, save it to disk, and return it."""
        wav_bytes = pcm_to_wav_bytes(
            pcm_chunk,
            channels=_CHANNELS,
            sample_width_bytes=_SAMPLE_WIDTH_BYTES,
            sample_rate_hz=self._sample_rate_hz,
        )
        logger.debug(
            "Built audio chunk #%d (%d bytes, %.2fs).",
            chunk_index,
            len(wav_bytes),
            len(pcm_chunk) / (self._sample_rate_hz * _SAMPLE_WIDTH_BYTES * _CHANNELS),
        )
        self._save_chunk(wav_bytes, chunk_index)
        return wav_bytes

    def _save_chunk(self, wav_bytes: bytes, chunk_index: int) -> None:
        if self._chunk_save_dir is None:
            return
        filename = f"chunk_{chunk_index:06d}_{datetime.now():%Y%m%d_%H%M%S_%f}.wav"
        path = self._chunk_save_dir / filename
        try:
            path.write_bytes(wav_bytes)
        except OSError as exc:
            # Failing to save a debug copy to disk should never interrupt
            # a live transcription session.
            logger.warning("Could not save audio chunk to %s: %s", path, exc)
    def stop(self) -> None:
        """
        Stop microphone capture gracefully.

        The stream() loop checks this flag and exits naturally,
        allowing the existing cleanup logic in the finally block
        to close the microphone and terminate PyAudio.
        """
        logger.info("Stopping microphone capture...")
        self._running = False

    @staticmethod
    def _close_stream(stream, pyaudio_instance: "pyaudio.PyAudio") -> None:
        try:
            if stream.is_active():
                stream.stop_stream()
            stream.close()
        except Exception:  # noqa: BLE001 - best-effort cleanup, never fatal
            logger.debug("Error while closing audio stream.", exc_info=True)
        finally:
            pyaudio_instance.terminate()
