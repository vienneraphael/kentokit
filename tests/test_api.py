"""Tests for the public token counting API."""

import typing as t

import httpx
import pytest

from kentokit import (
    AnthropicCountTokensRequest,
    OpenAICountTokensRequest,
    TokenCount,
    calc_tokens,
)
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


class DummyOpenAIProvider(ProviderBase):
    """OpenAI-specific provider stub for request-object tests."""

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
        input_data: str | None = None,
        model_ref: str | None = None,
        client: httpx.Client | None = None,
        request: OpenAICountTokensRequest | None = None,
    ) -> int:
        """Return a stable token count for OpenAI request-object tests.

        Parameters
        ----------
        input_data : str | None, default=None
            Plain text input, unused by the stub.
        model_ref : str | None, default=None
            Model reference, unused by the stub.
        client : httpx.Client | None, default=None
            Optional HTTP client, unused by the stub.
        request : OpenAICountTokensRequest | None, default=None
            Validated OpenAI request payload.

        Returns
        -------
        int
            Stable token count.
        """

        del client, input_data, model_ref
        assert request is not None
        assert request == OpenAICountTokensRequest(model="gpt-5-mini", input="hello")
        return 21


class DummyAnthropicProvider(ProviderBase):
    """Anthropic-specific provider stub for request-object tests."""

    provider_id = "anthropic"

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
        input_data: str | None = None,
        model_ref: str | None = None,
        client: httpx.Client | None = None,
        request: AnthropicCountTokensRequest | None = None,
    ) -> int:
        """Return a stable token count for Anthropic request-object tests.

        Parameters
        ----------
        input_data : str | None, default=None
            Plain text input, unused by the stub.
        model_ref : str | None, default=None
            Model reference, unused by the stub.
        client : httpx.Client | None, default=None
            Optional HTTP client, unused by the stub.
        request : AnthropicCountTokensRequest | None, default=None
            Validated Anthropic request payload.

        Returns
        -------
        int
            Stable token count.
        """

        del client, input_data, model_ref
        assert request is not None
        assert request == AnthropicCountTokensRequest(
            model="claude-sonnet-4-5",
            messages=[{"role": "user", "content": "hello"}],
            system="You are terse.",
            tools=[{"name": "lookup", "input_schema": {"type": "object"}}],
            tool_choice={"type": "auto"},
        )
        return 22


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


def test_calc_tokens_accepts_openai_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The public API should route OpenAI request objects to the OpenAI provider."""

    def fake_get_provider_class(*, provider_id: str) -> type[ProviderBase]:
        del provider_id
        return DummyOpenAIProvider

    monkeypatch.setattr("kentokit.api._get_provider_class", fake_get_provider_class)

    token_count = calc_tokens(
        input_data=OpenAICountTokensRequest(model="gpt-5-mini", input="hello"),
        provider_id="openai",
        api_key="secret",
    )

    assert token_count == TokenCount(total=21)


def test_calc_tokens_accepts_anthropic_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The public API should route Anthropic request objects to the provider."""

    def fake_get_provider_class(*, provider_id: str) -> type[ProviderBase]:
        del provider_id
        return DummyAnthropicProvider

    monkeypatch.setattr("kentokit.api._get_provider_class", fake_get_provider_class)

    token_count = calc_tokens(
        input_data=AnthropicCountTokensRequest(
            model="claude-sonnet-4-5",
            messages=[{"role": "user", "content": "hello"}],
            system="You are terse.",
            tools=[{"name": "lookup", "input_schema": {"type": "object"}}],
            tool_choice={"type": "auto"},
        ),
        provider_id="anthropic",
        api_key="secret",
    )

    assert token_count == TokenCount(total=22)


def test_calc_tokens_rejects_openai_request_for_other_providers() -> None:
    """The public API should fail early for incompatible request/provider pairs."""

    calc_tokens_runtime = t.cast(t.Callable[..., TokenCount], calc_tokens)

    with pytest.raises(TypeError, match="provider_id='openai'"):
        calc_tokens_runtime(
            input_data=OpenAICountTokensRequest(model="gpt-5-mini", input="hello"),
            provider_id="anthropic",
            api_key="secret",
        )


def test_calc_tokens_rejects_anthropic_request_for_other_providers() -> None:
    """The public API should fail early for incompatible request/provider pairs."""

    calc_tokens_runtime = t.cast(t.Callable[..., TokenCount], calc_tokens)

    with pytest.raises(TypeError, match="provider_id='anthropic'"):
        calc_tokens_runtime(
            input_data=AnthropicCountTokensRequest(
                model="claude-sonnet-4-5",
                messages=[{"role": "user", "content": "hello"}],
            ),
            provider_id="openai",
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
