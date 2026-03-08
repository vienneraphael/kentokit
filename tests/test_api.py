"""Tests for the public token counting API."""

import typing as t

import httpx
import pytest

from kentokit import TokenCount, calc_tokens
from kentokit.providers.base import (
    ProviderBase,
    TokenCountError,
)
from kentokit.providers.gemini import GeminiProvider


class DummyProvider(ProviderBase):
    """Provider stub for public API tests."""

    provider_id = "openai"

    def build_url(self, *, model_ref: str) -> str:
        """Build a dummy URL.

        Parameters
        ----------
        model_ref : str
            Provider-specific model identifier.

        Returns
        -------
        str
            Dummy URL.
        """

        del model_ref
        return "https://example.com"

    def build_payload(self, *, input_data: str, model_ref: str) -> dict[str, str]:
        """Build a dummy payload.

        Parameters
        ----------
        input_data : str
            Plain text input to count.
        model_ref : str
            Provider-specific model identifier.

        Returns
        -------
        dict[str, str]
            Dummy payload.
        """

        return {"input": input_data, "model": model_ref}

    def parse_token_count(self, *, data: dict[str, t.Any]) -> int:
        """Parse a dummy token count response.

        Parameters
        ----------
        data : dict[str, Any]
            Dummy response body.

        Returns
        -------
        int
            Parsed token count.
        """

        del data
        return 0

    def count_tokens(
        self,
        *,
        input_data: str,
        model_ref: str,
        client: httpx.Client | None = None,
    ) -> int:
        """Return a stable token count for public API tests.

        Parameters
        ----------
        input_data : str
            Plain text input to count.
        model_ref : str
            Provider-specific model identifier.
        client : httpx.Client | None, default=None
            Optional HTTP client, unused by the stub.

        Returns
        -------
        int
            Stable token count.
        """

        del input_data, model_ref, client
        return 42


def test_calc_tokens_returns_token_count(monkeypatch: pytest.MonkeyPatch) -> None:
    """The public API should wrap provider counts in TokenCount."""

    def fake_get_provider_class(*, provider_id: str) -> type[ProviderBase]:
        del provider_id
        return DummyProvider

    monkeypatch.setattr("kentokit.api._get_provider_class", fake_get_provider_class)

    token_count = calc_tokens(
        input_data="hello",
        model_ref="gpt-5-mini",
        provider_id="openai",
        api_key="secret",
    )

    assert token_count == TokenCount(total=42)
    assert token_count.total == 42


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

    with pytest.raises(TokenCountError, match="not valid JSON"):
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

    with pytest.raises(TokenCountError, match="totalTokens"):
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

    with pytest.raises(TokenCountError, match="status 429"):
        provider.count_tokens(
            input_data="hello",
            model_ref="gemini-2.0-flash",
            client=client,
        )

    client.close()
