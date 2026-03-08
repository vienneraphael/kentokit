"""Tests for OpenAI-specific request helpers."""

import typing as t

import httpx
import pytest

from kentokit import OpenAICountTokensRequest, TokenCount
from kentokit.providers.openai import OpenAIProvider


def test_openai_request_serializes_to_payload() -> None:
    """The request model should serialize to the OpenAI JSON payload."""

    request = OpenAICountTokensRequest(model="gpt-5-mini", input="hello")

    assert request.to_payload() == {
        "input": "hello",
        "model": "gpt-5-mini",
    }


@pytest.mark.parametrize("field_name", ["model", "input"])
def test_openai_request_rejects_non_string_fields(field_name: str) -> None:
    """The request model should validate runtime field types."""

    request_data: dict[str, t.Any] = {
        "input": "hello",
        "model": "gpt-5-mini",
    }
    request_data[field_name] = 1

    with pytest.raises(TypeError, match=f"{field_name} must be a string"):
        OpenAICountTokensRequest(
            model=request_data["model"],
            input=request_data["input"],
        )


def test_token_count_from_openai_uses_request_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The classmethod should route a validated request through OpenAIProvider."""

    def fake_count_tokens(
        self: OpenAIProvider,
        *,
        request: OpenAICountTokensRequest,
        client: httpx.Client | None = None,
        input_data: str | None = None,
        model_ref: str | None = None,
    ) -> int:
        del client, input_data, model_ref
        assert self.api_key == "secret"
        assert request == OpenAICountTokensRequest(model="gpt-5-mini", input="hello")
        return 18

    monkeypatch.setattr(OpenAIProvider, "count_tokens", fake_count_tokens)

    token_count = TokenCount.from_openai(
        model="gpt-5-mini",
        input="hello",
        api_key="secret",
    )

    assert token_count == TokenCount(total=18)
