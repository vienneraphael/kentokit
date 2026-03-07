"""Tests for provider-specific request and response handling."""

from __future__ import annotations

import json
import typing as t

import httpx

from kentokit.providers.anthropic import AnthropicProvider
from kentokit.providers.gemini import GeminiProvider
from kentokit.providers.openai import OpenAIProvider
from kentokit.providers.xai import XAIProvider


class RequestCapture(t.NamedTuple):
    """Captured request details for provider tests."""

    method: str
    url: str
    headers: dict[str, str]
    payload: dict[str, t.Any]


def test_openai_request_shape() -> None:
    """OpenAI provider should send the expected request."""

    captured_request: RequestCapture | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = _capture_request(request=request)
        return httpx.Response(status_code=200, json={"input_tokens": 12})

    provider = OpenAIProvider(api_key="secret")
    client = httpx.Client(transport=httpx.MockTransport(handler))

    token_count = provider.count_tokens(
        input_data="hello world",
        model_ref="gpt-5-mini",
        client=client,
    )

    client.close()

    assert token_count == 12
    assert captured_request is not None
    assert captured_request.method == "POST"
    assert captured_request.url == "https://api.openai.com/v1/responses/input_tokens"
    assert captured_request.headers["authorization"] == "Bearer secret"
    assert captured_request.headers["content-type"] == "application/json"
    assert captured_request.payload == {"input": "hello world", "model": "gpt-5-mini"}


def test_anthropic_request_shape() -> None:
    """Anthropic provider should send the expected request."""

    captured_request: RequestCapture | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = _capture_request(request=request)
        return httpx.Response(status_code=200, json={"input_tokens": 9})

    provider = AnthropicProvider(api_key="secret")
    client = httpx.Client(transport=httpx.MockTransport(handler))

    token_count = provider.count_tokens(
        input_data="hello world",
        model_ref="claude-sonnet-4-5",
        client=client,
    )

    client.close()

    assert token_count == 9
    assert captured_request is not None
    assert captured_request.method == "POST"
    assert captured_request.url == "https://api.anthropic.com/v1/messages/count_tokens"
    assert captured_request.headers["content-type"] == "application/json"
    assert captured_request.headers["x-api-key"] == "secret"
    assert captured_request.headers["anthropic-version"] == "2023-06-01"
    assert captured_request.payload == {
        "messages": [{"content": "hello world", "role": "user"}],
        "model": "claude-sonnet-4-5",
    }


def test_gemini_request_shape() -> None:
    """Gemini provider should send the expected request."""

    captured_request: RequestCapture | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = _capture_request(request=request)
        return httpx.Response(status_code=200, json={"totalTokens": 7})

    provider = GeminiProvider(api_key="secret")
    client = httpx.Client(transport=httpx.MockTransport(handler))

    token_count = provider.count_tokens(
        input_data="hello world",
        model_ref="gemini-2.0-flash",
        client=client,
    )

    client.close()

    assert token_count == 7
    assert captured_request is not None
    assert captured_request.method == "POST"
    assert (
        captured_request.url == "https://generativelanguage.googleapis.com/v1beta/"
        "models/gemini-2.0-flash:countTokens?key=secret"
    )
    assert captured_request.headers["content-type"] == "application/json"
    assert captured_request.payload == {
        "contents": [{"parts": [{"text": "hello world"}], "role": "user"}]
    }


def test_xai_request_shape() -> None:
    """xAI provider should send the expected request."""

    captured_request: RequestCapture | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = _capture_request(request=request)
        return httpx.Response(status_code=200, json={"token_ids": [1, 2, 3, 4]})

    provider = XAIProvider(api_key="secret")
    client = httpx.Client(transport=httpx.MockTransport(handler))

    token_count = provider.count_tokens(
        input_data="hello world",
        model_ref="grok-4-fast",
        client=client,
    )

    client.close()

    assert token_count == 4
    assert captured_request is not None
    assert captured_request.method == "POST"
    assert captured_request.url == "https://api.x.ai/v1/tokenize-text"
    assert captured_request.headers["authorization"] == "Bearer secret"
    assert captured_request.headers["content-type"] == "application/json"
    assert captured_request.payload == {"model": "grok-4-fast", "text": "hello world"}


def _capture_request(*, request: httpx.Request) -> RequestCapture:
    """Convert a request into a comparable structure.

    Parameters
    ----------
    request : httpx.Request
        Request captured by the mock transport.

    Returns
    -------
    RequestCapture
        Comparable request details.
    """

    return RequestCapture(
        method=request.method,
        url=str(request.url),
        headers={key.lower(): value for key, value in request.headers.items()},
        payload=json.loads(request.content.decode("utf-8")),
    )
