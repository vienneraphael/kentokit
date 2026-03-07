"""Tests for the public token counting API."""

import typing as t

import httpx
import pytest

from kentokit.api import calc_tokens
from kentokit.providers.base import (
    ProviderHTTPError,
    ProviderResponseError,
    UnsupportedProviderError,
)
from kentokit.providers.gemini import GeminiProvider


def test_calc_tokens_rejects_unknown_provider() -> None:
    """The public API should reject unknown providers."""

    with pytest.raises(UnsupportedProviderError, match="mistral"):
        calc_tokens(
            input_data="hello",
            model_ref="gpt-5-mini",
            provider_id=t.cast(t.Any, "mistral"),
            api_key="secret",
        )


def test_gemini_normalizes_model_reference() -> None:
    """Gemini URLs should not double-prefix model refs."""

    provider = GeminiProvider(api_key="secret")
    assert (
        provider.build_url(model_ref="gemini-2.0-flash")
        == "https://generativelanguage.googleapis.com/v1beta/"
        "models/gemini-2.0-flash:countTokens?key=secret"
    )
    assert (
        provider.build_url(model_ref="models/gemini-2.0-flash")
        == "https://generativelanguage.googleapis.com/v1beta/"
        "models/gemini-2.0-flash:countTokens?key=secret"
    )


def test_provider_raises_for_non_json_response() -> None:
    """Providers should reject non-JSON responses."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=200, text="not-json")

    provider = GeminiProvider(api_key="secret")
    client = httpx.Client(transport=httpx.MockTransport(handler))

    with pytest.raises(ProviderResponseError, match="not valid JSON"):
        provider.count_tokens(
            input_data="hello",
            model_ref="gemini-2.0-flash",
            client=client,
        )

    client.close()


def test_provider_raises_for_missing_count_field() -> None:
    """Providers should reject responses that omit count fields."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=200, json={})

    provider = GeminiProvider(api_key="secret")
    client = httpx.Client(transport=httpx.MockTransport(handler))

    with pytest.raises(ProviderResponseError, match="totalTokens"):
        provider.count_tokens(
            input_data="hello",
            model_ref="gemini-2.0-flash",
            client=client,
        )

    client.close()


def test_provider_raises_for_non_success_status() -> None:
    """Providers should raise HTTP errors for non-success responses."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=429, json={"error": "rate limited"})

    provider = GeminiProvider(api_key="secret")
    client = httpx.Client(transport=httpx.MockTransport(handler))

    with pytest.raises(ProviderHTTPError, match="status 429"):
        provider.count_tokens(
            input_data="hello",
            model_ref="gemini-2.0-flash",
            client=client,
        )

    client.close()
