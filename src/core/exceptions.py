"""
Custom exceptions for the Speech-to-Text subsystem.

Using a dedicated exception hierarchy lets callers (e.g. main.py) catch
subsystem-specific failures distinctly from unrelated bugs, and lets each
layer raise errors with context relevant to that layer without leaking
third-party exception types (e.g. from `pyaudio` or `openai`) outside of
their owning module.
"""


class SpeechToTextSubsystemError(Exception):
    """Base class for all errors raised by this subsystem."""


class AudioCaptureError(SpeechToTextSubsystemError):
    """Raised when audio cannot be captured from an `AudioSource`."""


class TranscriptionError(SpeechToTextSubsystemError):
    """Raised when a `SpeechToTextEngine` fails to transcribe audio."""
