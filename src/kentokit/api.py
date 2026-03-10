"""Public API for token counting."""

import typing as t

from kentokit.providers import PROVIDER_REGISTRY
from kentokit.providers.anthropic import AnthropicProvider
from kentokit.providers.base import ProviderBase, ProviderId, UnsupportedProviderError
from kentokit.providers.openai import OpenAIProvider
from kentokit.requests.anthropic import AnthropicCountTokensRequest
from kentokit.requests.openai import OpenAICountTokensRequest
from kentokit.token_count import TokenCount


@t.overload
def calc_tokens(
    *,
    input_data: AnthropicCountTokensRequest,
    provider_id: t.Literal["anthropic"],
    api_key: str,
    model_ref: None = None,
) -> TokenCount: ...


@t.overload
def calc_tokens(
    *,
    input_data: OpenAICountTokensRequest,
    provider_id: t.Literal["openai"],
    api_key: str,
    model_ref: None = None,
) -> TokenCount: ...


@t.overload
def calc_tokens(
    *,
    input_data: str,
    model_ref: str,
    provider_id: ProviderId,
    api_key: str,
) -> TokenCount: ...


def calc_tokens(
    *,
    input_data: str | AnthropicCountTokensRequest | OpenAICountTokensRequest,
    model_ref: str | None = None,
    provider_id: ProviderId,
    api_key: str,
) -> TokenCount:
    """Calculate the number of input tokens.

    Parameters
    ----------
    input_data : str | AnthropicCountTokensRequest | OpenAICountTokensRequest
        Plain text input for any provider, or a validated provider-native request
        payload for Anthropic or OpenAI when ``provider_id`` matches that
        request type.
    model_ref : str | None, default=None
        Provider-specific model identifier for plain-text requests. Omit when
        ``input_data`` is an ``OpenAICountTokensRequest``.
    provider_id : ProviderId
        Provider identifier used to resolve the provider implementation.
    api_key : str
        API key used to authenticate the request.

    Returns
    -------
    TokenCount
        Normalized token count reported by the provider.

    Raises
    ------
    UnsupportedProviderError
        If ``provider_id`` is not supported.
    TokenCountError
        If the provider request fails or the response cannot be parsed.
    TypeError
        If ``input_data`` and ``provider_id`` are incompatible.
    """

    if isinstance(input_data, AnthropicCountTokensRequest):
        if provider_id != "anthropic":
            raise TypeError(
                "AnthropicCountTokensRequest is only supported when provider_id='anthropic'"
            )
        if model_ref is not None:
            raise TypeError(
                "model_ref cannot be provided when input_data is an AnthropicCountTokensRequest"
            )

        provider_class = t.cast(
            type[AnthropicProvider],
            _get_provider_class(provider_id=provider_id),
        )
        provider = provider_class(api_key=api_key)
        return TokenCount(total=provider.count_tokens(request=input_data))

    if isinstance(input_data, OpenAICountTokensRequest):
        if provider_id != "openai":
            raise TypeError("OpenAICountTokensRequest is only supported when provider_id='openai'")
        if model_ref is not None:
            raise TypeError(
                "model_ref cannot be provided when input_data is an OpenAICountTokensRequest"
            )

        provider_class = t.cast(
            type[OpenAIProvider],
            _get_provider_class(provider_id=provider_id),
        )
        provider = provider_class(api_key=api_key)
        return TokenCount(total=provider.count_tokens(request=input_data))

    if model_ref is None:
        raise TypeError("model_ref must be provided when input_data is a string")

    provider_class = _get_provider_class(provider_id=provider_id)
    provider = provider_class(api_key=api_key)
    return TokenCount(total=provider.count_tokens(input_data=input_data, model_ref=model_ref))


def _get_provider_class(*, provider_id: str) -> type[ProviderBase]:
    """Resolve the provider class for a provider id.

    Parameters
    ----------
    provider_id : str
        Provider identifier supplied to the public API.

    Returns
    -------
    type[ProviderBase]
        Provider implementation class matching ``provider_id``.

    Raises
    ------
    UnsupportedProviderError
        If ``provider_id`` is not registered.
    """

    provider_class = PROVIDER_REGISTRY.get(t.cast(ProviderId, provider_id))
    if provider_class is None:
        raise UnsupportedProviderError(provider_id=provider_id)
    return provider_class
