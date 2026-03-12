"""Public Gemini modality enum."""

from enum import StrEnum


class GeminiModality(StrEnum):
    """Gemini modality values returned in token-count breakdowns."""

    MODALITY_UNSPECIFIED = "MODALITY_UNSPECIFIED"
    TEXT = "TEXT"
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    AUDIO = "AUDIO"
    DOCUMENT = "DOCUMENT"


__all__ = ["GeminiModality"]
