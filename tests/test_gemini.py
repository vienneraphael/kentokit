"""Tests for Gemini-specific request helpers."""

import typing as t

import httpx
import pytest

from kentokit import GeminiCountTokensRequest, TokenCount
from kentokit.providers.gemini import GeminiProvider


def test_gemini_request_serializes_contents_to_payload() -> None:
    """The request model should serialize direct Gemini contents payloads."""

    request = GeminiCountTokensRequest(
        model="gemini-2.0-flash",
        contents=[{"role": "user", "parts": [{"text": "hello"}]}],
    )

    assert request.to_payload() == {
        "contents": [{"role": "user", "parts": [{"text": "hello"}]}],
    }


def test_gemini_request_serializes_generate_content_request_to_payload() -> None:
    """The request model should serialize full Gemini generate requests."""

    request = GeminiCountTokensRequest(
        model="gemini-2.0-flash",
        generate_content_request={
            "contents": [{"role": "user", "parts": [{"text": "hello"}]}],
            "systemInstruction": {"parts": [{"text": "You are terse."}]},
        },
    )

    assert request.to_payload() == {
        "generateContentRequest": {
            "contents": [{"role": "user", "parts": [{"text": "hello"}]}],
            "systemInstruction": {"parts": [{"text": "You are terse."}]},
        }
    }


@pytest.mark.parametrize(
    ("request_kwargs", "message"),
    [
        (
            {
                "model": 1,
                "contents": [{"role": "user", "parts": [{"text": "hello"}]}],
            },
            "model must be a string",
        ),
        (
            {
                "model": "gemini-2.0-flash",
                "contents": "hello",
            },
            "contents must be a list or None",
        ),
        (
            {
                "model": "gemini-2.0-flash",
                "contents": ["hello"],
            },
            "contents must contain dictionaries",
        ),
        (
            {
                "model": "gemini-2.0-flash",
                "generate_content_request": "hello",
            },
            "generate_content_request must be a dictionary or None",
        ),
        (
            {
                "model": "gemini-2.0-flash",
            },
            "exactly one of contents or generate_content_request must be provided",
        ),
        (
            {
                "model": "gemini-2.0-flash",
                "contents": [{"role": "user", "parts": [{"text": "hello"}]}],
                "generate_content_request": {
                    "contents": [{"role": "user", "parts": [{"text": "hello"}]}]
                },
            },
            "exactly one of contents or generate_content_request must be provided",
        ),
    ],
)
def test_gemini_request_rejects_invalid_fields(
    request_kwargs: dict[str, t.Any],
    message: str,
) -> None:
    """The request model should validate Gemini top-level field types."""

    with pytest.raises(TypeError, match=message):
        GeminiCountTokensRequest(**request_kwargs)


def test_token_count_from_gemini_uses_request_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The classmethod should route a validated request through GeminiProvider."""

    def fake_count_tokens(
        self: GeminiProvider,
        *,
        request: GeminiCountTokensRequest,
        client: httpx.Client | None = None,
        input_data: str | None = None,
        model_ref: str | None = None,
    ) -> int:
        del client, input_data, model_ref
        assert self.api_key == "secret"
        assert request == GeminiCountTokensRequest(
            model="gemini-2.0-flash",
            contents=[{"role": "user", "parts": [{"text": "hello"}]}],
        )
        return 17

    monkeypatch.setattr(GeminiProvider, "count_tokens", fake_count_tokens)

    token_count = TokenCount.from_gemini(
        model="gemini-2.0-flash",
        api_key="secret",
        contents=[{"role": "user", "parts": [{"text": "hello"}]}],
    )

    assert token_count == TokenCount(total=17)
