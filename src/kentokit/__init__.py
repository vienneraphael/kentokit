"""kentokit public package surface."""

from kentokit.api import calc_tokens
from kentokit.providers.base import (
    ProviderId,
    TokenCountError,
    UnsupportedProviderError,
)

__all__ = [
    "ProviderId",
    "TokenCountError",
    "UnsupportedProviderError",
    "calc_tokens",
    "main",
]


def main() -> None:
    """Run the package entrypoint."""
    print("Hello from kentokit!")
