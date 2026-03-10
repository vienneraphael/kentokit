"""Tests for xAI-specific request helpers."""

import typing as t

import httpx
import pytest

from kentokit import TokenCount, XAICountTokensRequest
from kentokit.providers.xai import XAIProvider


def test_xai_request_serializes_to_payload() -> None:
    """The request model should serialize to the xAI JSON payload."""

    request = XAICountTokensRequest(model="grok-4-fast", text="hello")

    assert request.to_payload() == {
        "model": "grok-4-fast",
        "text": "hello",
    }


@pytest.mark.parametrize("field_name", ["model", "text"])
def test_xai_request_rejects_non_string_fields(field_name: str) -> None:
    """The request model should validate runtime field types."""

    request_data: dict[str, t.Any] = {
        "model": "grok-4-fast",
        "text": "hello",
    }
    request_data[field_name] = 1

    with pytest.raises(TypeError, match=f"{field_name} must be a string"):
        XAICountTokensRequest(
            model=request_data["model"],
            text=request_data["text"],
        )


def test_token_count_from_xai_uses_request_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The classmethod should route a validated request through XAIProvider."""

    def fake_count_tokens(
        self: XAIProvider,
        *,
        request: XAICountTokensRequest,
        client: httpx.Client | None = None,
        input_data: str | None = None,
        model_ref: str | None = None,
    ) -> int:
        del client, input_data, model_ref
        assert self.api_key == "secret"
        assert request == XAICountTokensRequest(model="grok-4-fast", text="hello")
        return 11

    monkeypatch.setattr(XAIProvider, "count_tokens", fake_count_tokens)

    token_count = TokenCount.from_xai(
        model="grok-4-fast",
        text="hello",
        api_key="secret",
    )

    assert token_count == TokenCount(total=11)
