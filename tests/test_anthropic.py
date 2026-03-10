"""Tests for Anthropic-specific request helpers."""

import typing as t

import httpx
import pytest

from kentokit import AnthropicCountTokensRequest, TokenCount
from kentokit.providers.anthropic import AnthropicProvider


def test_anthropic_request_serializes_to_payload() -> None:
    """The request model should serialize to the Anthropic JSON payload."""

    request = AnthropicCountTokensRequest(
        model="claude-sonnet-4-5",
        messages=[{"role": "user", "content": "hello"}],
        system="You are terse.",
        tools=[{"name": "lookup", "input_schema": {"type": "object"}}],
        tool_choice={"type": "auto"},
    )

    assert request.to_payload() == {
        "messages": [{"role": "user", "content": "hello"}],
        "model": "claude-sonnet-4-5",
        "system": "You are terse.",
        "tools": [{"name": "lookup", "input_schema": {"type": "object"}}],
        "tool_choice": {"type": "auto"},
    }


def test_anthropic_request_omits_optional_fields_when_unset() -> None:
    """Unset optional Anthropic fields should not appear in the payload."""

    request = AnthropicCountTokensRequest(
        model="claude-sonnet-4-5",
        messages=[{"role": "user", "content": "hello"}],
    )

    assert request.to_payload() == {
        "messages": [{"role": "user", "content": "hello"}],
        "model": "claude-sonnet-4-5",
    }


@pytest.mark.parametrize(
    ("request_kwargs", "message"),
    [
        (
            {
                "model": 1,
                "messages": [{"role": "user", "content": "hello"}],
            },
            "model must be a string",
        ),
        (
            {
                "model": "claude-sonnet-4-5",
                "messages": "hello",
            },
            "messages must be a list",
        ),
        (
            {
                "model": "claude-sonnet-4-5",
                "messages": ["hello"],
            },
            "messages must contain dictionaries",
        ),
        (
            {
                "model": "claude-sonnet-4-5",
                "messages": [{"role": "user", "content": "hello"}],
                "system": 1,
            },
            "system must be a string, a list, or None",
        ),
        (
            {
                "model": "claude-sonnet-4-5",
                "messages": [{"role": "user", "content": "hello"}],
                "system": ["hello"],
            },
            "system lists must contain dictionaries",
        ),
        (
            {
                "model": "claude-sonnet-4-5",
                "messages": [{"role": "user", "content": "hello"}],
                "tools": "lookup",
            },
            "tools must be a list or None",
        ),
        (
            {
                "model": "claude-sonnet-4-5",
                "messages": [{"role": "user", "content": "hello"}],
                "tools": ["lookup"],
            },
            "tools must contain dictionaries",
        ),
        (
            {
                "model": "claude-sonnet-4-5",
                "messages": [{"role": "user", "content": "hello"}],
                "tool_choice": "auto",
            },
            "tool_choice must be a dictionary or None",
        ),
    ],
)
def test_anthropic_request_rejects_invalid_field_types(
    request_kwargs: dict[str, t.Any],
    message: str,
) -> None:
    """The request model should validate Anthropic field container types."""

    with pytest.raises(TypeError, match=message):
        AnthropicCountTokensRequest(**request_kwargs)


def test_token_count_from_anthropic_uses_request_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The classmethod should route a validated request through AnthropicProvider."""

    def fake_count_tokens(
        self: AnthropicProvider,
        *,
        request: AnthropicCountTokensRequest,
        client: httpx.Client | None = None,
        input_data: str | None = None,
        model_ref: str | None = None,
    ) -> int:
        del client, input_data, model_ref
        assert self.api_key == "secret"
        assert request == AnthropicCountTokensRequest(
            model="claude-sonnet-4-5",
            messages=[{"role": "user", "content": "hello"}],
            system="You are terse.",
            tools=[{"name": "lookup", "input_schema": {"type": "object"}}],
            tool_choice={"type": "auto"},
        )
        return 23

    monkeypatch.setattr(AnthropicProvider, "count_tokens", fake_count_tokens)

    token_count = TokenCount.from_anthropic(
        model="claude-sonnet-4-5",
        messages=[{"role": "user", "content": "hello"}],
        api_key="secret",
        system="You are terse.",
        tools=[{"name": "lookup", "input_schema": {"type": "object"}}],
        tool_choice={"type": "auto"},
    )

    assert token_count == TokenCount(total=23)
