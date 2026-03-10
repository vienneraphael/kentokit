"""Normalized token count model."""

import typing as t
from dataclasses import dataclass

from kentokit.providers.anthropic import AnthropicProvider
from kentokit.providers.gemini import GeminiProvider
from kentokit.providers.openai import OpenAIProvider
from kentokit.requests.anthropic import AnthropicCountTokensRequest
from kentokit.requests.gemini import GeminiCountTokensRequest
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
    def from_anthropic(
        cls,
        *,
        model: str,
        messages: list[dict[str, t.Any]],
        api_key: str,
        system: str | list[dict[str, t.Any]] | None = None,
        tools: list[dict[str, t.Any]] | None = None,
        tool_choice: dict[str, t.Any] | None = None,
    ) -> t.Self:
        """Count Anthropic input tokens from a validated request shape.

        Parameters
        ----------
        model : str
            Anthropic model identifier.
        messages : list[dict[str, Any]]
            Anthropic Messages API payload blocks.
        api_key : str
            Anthropic API key used for the provider transport.
        system : str | list[dict[str, Any]] | None, default=None
            Optional Anthropic system prompt content.
        tools : list[dict[str, Any]] | None, default=None
            Optional Anthropic tool definitions.
        tool_choice : dict[str, Any] | None, default=None
            Optional Anthropic tool choice configuration.

        Returns
        -------
        Self
            Normalized token count returned by the Anthropic provider.
        """

        request = AnthropicCountTokensRequest(
            model=model,
            messages=messages,
            system=system,
            tools=tools,
            tool_choice=tool_choice,
        )
        provider = AnthropicProvider(api_key=api_key)
        total = provider.count_tokens(request=request)
        return cls(total=total)

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

    @classmethod
    def from_gemini(
        cls,
        *,
        model: str,
        api_key: str,
        contents: list[dict[str, t.Any]] | None = None,
        generate_content_request: dict[str, t.Any] | None = None,
    ) -> t.Self:
        """Count Gemini input tokens from a validated request shape.

        Parameters
        ----------
        model : str
            Gemini model identifier.
        api_key : str
            Gemini API key used for the provider transport.
        contents : list[dict[str, Any]] | None, default=None
            Optional Gemini contents payload sent directly to ``countTokens``.
        generate_content_request : dict[str, Any] | None, default=None
            Optional full Gemini ``generateContentRequest`` payload.

        Returns
        -------
        Self
            Normalized token count returned by the Gemini provider.
        """

        request = GeminiCountTokensRequest(
            model=model,
            contents=contents,
            generate_content_request=generate_content_request,
        )
        provider = GeminiProvider(api_key=api_key)
        total = provider.count_tokens(request=request)
        return cls(total=total)
