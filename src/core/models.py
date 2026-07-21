"""
Shared data models used across the Speech-to-Text subsystem.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Transcript:
    """
    Represents a single piece of transcribed text.

    Attributes:
        text: The transcribed text.
        is_final: Whether this transcript is a final result (True) or an
            interim/partial result that may still change (False).
        timestamp: When the transcript was produced.
    """

    text: str
    is_final: bool = True
    timestamp: datetime = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            object.__setattr__(self, "timestamp", datetime.now())
