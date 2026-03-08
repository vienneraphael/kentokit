"""Normalized token count model."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TokenCount:
    """Normalized token count returned by the public API.

    Parameters
    ----------
    total : int
        Total token count reported by the provider.
    """

    total: int
