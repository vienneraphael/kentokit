"""Normalized token count model."""

import typing as t
from dataclasses import dataclass

from kentokit.providers.anthropic import AnthropicProvider
from kentokit.providers.gemini import GeminiProvider
from kentokit.providers.openai import OpenAIProvider
from kentokit.providers.xai import XAIProvider
from kentokit.requests.anthropic import AnthropicCountTokensRequest
from kentokit.requests.gemini import GeminiCountTokensRequest
from kentokit.requests.openai import OpenAICountTokensRequest
from kentokit.requests.xai import XAICountTokensRequest


@dataclass(frozen=True, slots=True)
class TokenCount:
    """Normalized token count returned by the public API.

    Parameters
    ----------
    total : int
        Total token count reported by the provider.
    cached_tokens : int | None, default=None
        Gemini cached token count when the provider returns it.
    token_details : list[dict[str, Any]] | None, default=None
        Gemini modality breakdown for prompt-side tokens.
    cache_token_details : list[dict[str, Any]] | None, default=None
        Gemini modality breakdown for cached tokens.
    """

    total: int
    cached_tokens: int | None = None
    token_details: list[dict[str, t.Any]] | None = None
    cache_token_details: list[dict[str, t.Any]] | None = None

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
        api_key: str,
        input: str | list[dict[str, t.Any]] | None = None,
        conversation: str | dict[str, t.Any] | None = None,
        instructions: str | None = None,
        parallel_tool_calls: bool | None = None,
        previous_response_id: str | None = None,
        reasoning: dict[str, t.Any] | None = None,
        text: dict[str, t.Any] | None = None,
        tool_choice: str | dict[str, t.Any] | None = None,
        tools: list[dict[str, t.Any]] | None = None,
        truncation: t.Literal["auto", "disabled"] | None = None,
    ) -> t.Self:
        """Count OpenAI input tokens from a validated request shape.

        Parameters
        ----------
        model : str
            OpenAI model identifier.
        api_key : str
            OpenAI API key used for the provider transport.
        input : str | list[dict[str, Any]] | None, default=None
            Optional Responses-style input sent to the count-tokens endpoint.
        conversation : str | dict[str, Any] | None, default=None
            Optional OpenAI conversation state for the count request.
        instructions : str | None, default=None
            Optional system or developer instructions applied to the request.
        parallel_tool_calls : bool | None, default=None
            Optional OpenAI parallel tool-calling setting.
        previous_response_id : str | None, default=None
            Optional prior response id used to continue an OpenAI conversation.
        reasoning : dict[str, Any] | None, default=None
            Optional OpenAI reasoning configuration.
        text : dict[str, Any] | None, default=None
            Optional OpenAI text output configuration.
        tool_choice : str | dict[str, Any] | None, default=None
            Optional OpenAI tool choice configuration.
        tools : list[dict[str, Any]] | None, default=None
            Optional OpenAI tool definitions.
        truncation : Literal["auto", "disabled"] | None, default=None
            Optional OpenAI truncation mode for the count request.

        Returns
        -------
        Self
            Normalized token count returned by the OpenAI provider.
        """

        request = OpenAICountTokensRequest(
            model=model,
            input=input,
            conversation=conversation,
            instructions=instructions,
            parallel_tool_calls=parallel_tool_calls,
            previous_response_id=previous_response_id,
            reasoning=reasoning,
            text=text,
            tool_choice=tool_choice,
            tools=tools,
            truncation=truncation,
        )
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
        token_count = provider.count_token_count(request=request)
        return cls(
            total=token_count.total,
            cached_tokens=token_count.cached_tokens,
            token_details=token_count.token_details,
            cache_token_details=token_count.cache_token_details,
        )

    @classmethod
    def from_xai(
        cls,
        *,
        model: str,
        text: str,
        api_key: str,
    ) -> t.Self:
        """Count xAI input tokens from a validated request shape.

        Parameters
        ----------
        model : str
            xAI model identifier.
        text : str
            Input text sent to the xAI tokenization endpoint.
        api_key : str
            xAI API key used for the provider transport.

        Returns
        -------
        Self
            Normalized token count returned by the xAI provider.
        """

        request = XAICountTokensRequest(model=model, text=text)
        provider = XAIProvider(api_key=api_key)
        total = provider.count_tokens(request=request)
        return cls(total=total)
