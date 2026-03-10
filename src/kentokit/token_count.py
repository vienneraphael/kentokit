"""Normalized token count model."""

import typing as t
from dataclasses import dataclass

from kentokit.providers.openai import OpenAIProvider
from kentokit.requests.openai import OpenAICountTokensRequest


@dataclass(frozen=True, slots=True)
class TokenCount:
    """Normalized token count returned by the public API.

    Parameters
    ----------
    total : int
        Total token count reported by the provider.
    """

    total: int

    @classmethod
    def from_openai(
        cls,
        *,
        model: str,
        input: str,
        api_key: str,
    ) -> t.Self:
        """Count OpenAI input tokens from a validated request shape.

        Parameters
        ----------
        model : str
            OpenAI model identifier.
        input : str
            Input text sent to the OpenAI count-tokens endpoint.
        api_key : str
            OpenAI API key used for the provider transport.

        Returns
        -------
        Self
            Normalized token count returned by the OpenAI provider.
        """

        request = OpenAICountTokensRequest(model=model, input=input)
        provider = OpenAIProvider(api_key=api_key)
        total = provider.count_tokens(request=request)
        return cls(total=total)
