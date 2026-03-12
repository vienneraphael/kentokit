"""Tests for provider-specific request and response handling."""

from __future__ import annotations

import json
import re
import typing as t

import httpx
import pytest

from kentokit import GeminiModality, TokenCount
from kentokit.providers.anthropic import AnthropicProvider
from kentokit.providers.base import TokenCountError
from kentokit.providers.gemini import GeminiProvider
from kentokit.providers.openai import OpenAIProvider
from kentokit.providers.xai import XAIProvider
from kentokit.requests.anthropic import AnthropicCountTokensRequest
from kentokit.requests.gemini import GeminiCountTokensRequest
from kentokit.requests.openai import OpenAICountTokensRequest
from kentokit.requests.xai import XAICountTokensRequest


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


def test_openai_request_object_shape() -> None:
    """OpenAI provider should accept validated request objects."""

    captured_request: RequestCapture | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = _capture_request(request=request)
        return httpx.Response(status_code=200, json={"input_tokens": 13})

    provider = OpenAIProvider(api_key="secret")
    client = httpx.Client(transport=httpx.MockTransport(handler))

    token_count = provider.count_tokens(
        request=OpenAICountTokensRequest(
            model="gpt-5-mini",
            input=[
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": "hello world"}],
                }
            ],
            conversation="conv_123",
            instructions="You are terse.",
            parallel_tool_calls=False,
            previous_response_id="resp_123",
            reasoning={"effort": "low"},
            text={"format": {"type": "text"}},
            tool_choice="auto",
            tools=[{"type": "function", "name": "lookup"}],
            truncation="disabled",
        ),
        client=client,
    )

    client.close()

    assert token_count == 13
    assert captured_request is not None
    assert captured_request.method == "POST"
    assert captured_request.url == "https://api.openai.com/v1/responses/input_tokens"
    assert captured_request.headers["authorization"] == "Bearer secret"
    assert captured_request.headers["content-type"] == "application/json"
    assert captured_request.payload == {
        "conversation": "conv_123",
        "input": [
            {
                "role": "user",
                "content": [{"type": "input_text", "text": "hello world"}],
            }
        ],
        "instructions": "You are terse.",
        "model": "gpt-5-mini",
        "parallel_tool_calls": False,
        "previous_response_id": "resp_123",
        "reasoning": {"effort": "low"},
        "text": {"format": {"type": "text"}},
        "tool_choice": "auto",
        "tools": [{"type": "function", "name": "lookup"}],
        "truncation": "disabled",
    }


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


def test_anthropic_request_object_shape() -> None:
    """Anthropic provider should accept validated request objects."""

    captured_request: RequestCapture | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = _capture_request(request=request)
        return httpx.Response(status_code=200, json={"input_tokens": 10})

    provider = AnthropicProvider(api_key="secret")
    client = httpx.Client(transport=httpx.MockTransport(handler))

    token_count = provider.count_tokens(
        request=AnthropicCountTokensRequest(
            model="claude-sonnet-4-5",
            messages=[{"role": "user", "content": "hello world"}],
            system="You are terse.",
            tools=[{"name": "lookup", "input_schema": {"type": "object"}}],
            tool_choice={"type": "auto"},
        ),
        client=client,
    )

    client.close()

    assert token_count == 10
    assert captured_request is not None
    assert captured_request.method == "POST"
    assert captured_request.url == "https://api.anthropic.com/v1/messages/count_tokens"
    assert captured_request.headers["content-type"] == "application/json"
    assert captured_request.headers["x-api-key"] == "secret"
    assert captured_request.headers["anthropic-version"] == "2023-06-01"
    assert captured_request.payload == {
        "messages": [{"role": "user", "content": "hello world"}],
        "model": "claude-sonnet-4-5",
        "system": "You are terse.",
        "tools": [{"name": "lookup", "input_schema": {"type": "object"}}],
        "tool_choice": {"type": "auto"},
    }


def test_anthropic_request_object_rejects_mixed_arguments() -> None:
    """Anthropic request objects should not be mixed with plain-text arguments."""

    provider = AnthropicProvider(api_key="secret")
    count_tokens_runtime = t.cast(t.Callable[..., int], provider.count_tokens)

    with pytest.raises(TypeError, match="request cannot be combined"):
        count_tokens_runtime(
            request=AnthropicCountTokensRequest(
                model="claude-sonnet-4-5",
                messages=[{"role": "user", "content": "hello world"}],
            ),
            input_data="hello world",
        )


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


def test_gemini_request_object_accepts_contents() -> None:
    """Gemini provider should accept validated contents request objects."""

    captured_request: RequestCapture | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = _capture_request(request=request)
        return httpx.Response(status_code=200, json={"totalTokens": 8})

    provider = GeminiProvider(api_key="secret")
    client = httpx.Client(transport=httpx.MockTransport(handler))

    token_count = provider.count_tokens(
        request=GeminiCountTokensRequest(
            model="gemini-2.0-flash",
            contents=[{"role": "user", "parts": [{"text": "hello world"}]}],
        ),
        client=client,
    )

    client.close()

    assert token_count == 8
    assert captured_request is not None
    assert captured_request.method == "POST"
    assert (
        captured_request.url == "https://generativelanguage.googleapis.com/v1beta/"
        "models/gemini-2.0-flash:countTokens?key=secret"
    )
    assert captured_request.headers["content-type"] == "application/json"
    assert captured_request.payload == {
        "contents": [{"role": "user", "parts": [{"text": "hello world"}]}]
    }


def test_gemini_request_object_accepts_generate_content_request() -> None:
    """Gemini provider should accept full generateContentRequest payloads."""

    captured_request: RequestCapture | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = _capture_request(request=request)
        return httpx.Response(status_code=200, json={"totalTokens": 11})

    provider = GeminiProvider(api_key="secret")
    client = httpx.Client(transport=httpx.MockTransport(handler))

    token_count = provider.count_tokens(
        request=GeminiCountTokensRequest(
            model="models/gemini-2.0-flash",
            generate_content_request={
                "contents": [{"role": "user", "parts": [{"text": "hello world"}]}],
                "systemInstruction": {"parts": [{"text": "You are terse."}]},
            },
        ),
        client=client,
    )

    client.close()

    assert token_count == 11
    assert captured_request is not None
    assert captured_request.method == "POST"
    assert (
        captured_request.url == "https://generativelanguage.googleapis.com/v1beta/"
        "models/gemini-2.0-flash:countTokens?key=secret"
    )
    assert captured_request.headers["content-type"] == "application/json"
    assert captured_request.payload == {
        "generateContentRequest": {
            "contents": [{"role": "user", "parts": [{"text": "hello world"}]}],
            "systemInstruction": {"parts": [{"text": "You are terse."}]},
        }
    }


def test_gemini_count_token_count_returns_full_metadata() -> None:
    """Gemini should parse the full countTokens response into TokenCount."""

    def handler(request: httpx.Request) -> httpx.Response:
        del request
        return httpx.Response(
            status_code=200,
            json={
                "totalTokens": 17,
                "cachedContentTokenCount": 5,
                "promptTokensDetails": [
                    {"modality": "TEXT", "tokenCount": 12},
                    {"modality": "IMAGE", "tokenCount": 5},
                ],
                "cacheTokensDetails": [
                    {"modality": "TEXT", "tokenCount": 5},
                ],
            },
        )

    provider = GeminiProvider(api_key="secret")
    client = httpx.Client(transport=httpx.MockTransport(handler))

    token_count = provider.count_token_count(
        input_data="hello world",
        model_ref="gemini-2.0-flash",
        client=client,
    )

    client.close()

    assert token_count == TokenCount(
        total=17,
        cached_tokens=5,
        token_details=[
            {"modality": GeminiModality.TEXT, "tokenCount": 12},
            {"modality": GeminiModality.IMAGE, "tokenCount": 5},
        ],
        cache_token_details=[
            {"modality": GeminiModality.TEXT, "tokenCount": 5},
        ],
    )


def test_gemini_request_object_rejects_mixed_arguments() -> None:
    """Gemini request objects should not be mixed with plain-text arguments."""

    provider = GeminiProvider(api_key="secret")
    count_tokens_runtime = t.cast(t.Callable[..., int], provider.count_tokens)

    with pytest.raises(TypeError, match="request cannot be combined"):
        count_tokens_runtime(
            request=GeminiCountTokensRequest(
                model="gemini-2.0-flash",
                contents=[{"role": "user", "parts": [{"text": "hello world"}]}],
            ),
            input_data="hello world",
        )


@pytest.mark.parametrize(
    ("response_json", "message"),
    [
        ({}, "totalTokens"),
        ({"totalTokens": "7"}, "totalTokens"),
        (
            {"totalTokens": 7, "cachedContentTokenCount": "5"},
            "cachedContentTokenCount",
        ),
        (
            {"totalTokens": 7, "promptTokensDetails": "bad"},
            "promptTokensDetails",
        ),
        (
            {"totalTokens": 7, "cacheTokensDetails": "bad"},
            "cacheTokensDetails",
        ),
        (
            {"totalTokens": 7, "promptTokensDetails": ["bad"]},
            "promptTokensDetails[0]",
        ),
        (
            {"totalTokens": 7, "promptTokensDetails": [{}]},
            "promptTokensDetails[0].modality",
        ),
        (
            {
                "totalTokens": 7,
                "promptTokensDetails": [{"modality": "NOT_A_MODALITY", "tokenCount": 3}],
            },
            "promptTokensDetails[0].modality",
        ),
        (
            {
                "totalTokens": 7,
                "promptTokensDetails": [{"modality": "TEXT"}],
            },
            "promptTokensDetails[0].tokenCount",
        ),
    ],
)
def test_gemini_count_token_count_rejects_invalid_metadata(
    response_json: dict[str, t.Any],
    message: str,
) -> None:
    """Gemini should validate the full metadata response shape."""

    def handler(request: httpx.Request) -> httpx.Response:
        del request
        return httpx.Response(status_code=200, json=response_json)

    provider = GeminiProvider(api_key="secret")
    client = httpx.Client(transport=httpx.MockTransport(handler))

    with pytest.raises(TokenCountError, match=re.escape(message)):
        provider.count_token_count(
            input_data="hello world",
            model_ref="gemini-2.0-flash",
            client=client,
        )

    client.close()


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


def test_xai_request_object_shape() -> None:
    """xAI provider should send the expected request payload from request objects."""

    captured_request: RequestCapture | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = _capture_request(request=request)
        return httpx.Response(status_code=200, json={"token_ids": [1, 2, 3, 4]})

    provider = XAIProvider(api_key="secret")
    client = httpx.Client(transport=httpx.MockTransport(handler))

    token_count = provider.count_tokens(
        request=XAICountTokensRequest(
            model="grok-4-fast",
            text="hello world",
        ),
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


def test_xai_request_object_rejects_mixed_arguments() -> None:
    """xAI request objects should not be mixed with plain-text arguments."""

    provider = XAIProvider(api_key="secret")
    count_tokens_runtime = t.cast(t.Callable[..., int], provider.count_tokens)

    with pytest.raises(TypeError, match="request cannot be combined"):
        count_tokens_runtime(
            request=XAICountTokensRequest(
                model="grok-4-fast",
                text="hello world",
            ),
            input_data="hello world",
        )


def test_xai_counts_non_integer_token_arrays() -> None:
    """xAI token counts should be derived from array length only."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            json={"token_ids": ["hello", "world", "!"]},
        )

    provider = XAIProvider(api_key="secret")
    client = httpx.Client(transport=httpx.MockTransport(handler))

    token_count = provider.count_tokens(
        input_data="hello world",
        model_ref="grok-4-fast",
        client=client,
    )

    client.close()

    assert token_count == 3


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
