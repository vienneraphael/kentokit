"""Public API for token counting."""

import typing as t

from kentokit.providers import PROVIDER_REGISTRY
from kentokit.providers.base import ProviderBase, ProviderId, UnsupportedProviderError
from kentokit.token_count import TokenCount


def calc_tokens(
    *,
    input_data: str,
    model_ref: str,
    provider_id: ProviderId,
    api_key: str,
) -> TokenCount:
    """Calculate the number of input tokens for plain text.

    Parameters
    ----------
    input_data : str
        Plain text input to send to the provider token counting endpoint.
    model_ref : str
        Provider-specific model identifier.
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
    """

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
