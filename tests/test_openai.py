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


def test_openai_request_serializes_message_array_input() -> None:
    """The request model should preserve Responses-style message-array input."""

    request = OpenAICountTokensRequest(
        model="gpt-5-mini",
        input=[
            {
                "role": "user",
                "content": [{"type": "input_text", "text": "hello"}],
            }
        ],
    )

    assert request.to_payload() == {
        "input": [
            {
                "role": "user",
                "content": [{"type": "input_text", "text": "hello"}],
            }
        ],
        "model": "gpt-5-mini",
    }


def test_openai_request_serializes_optional_count_fields() -> None:
    """The request model should include supported optional OpenAI fields."""

    request = OpenAICountTokensRequest(
        model="gpt-5-mini",
        conversation={"id": "conv_123"},
        instructions="You are terse.",
        parallel_tool_calls=True,
        previous_response_id="resp_123",
        reasoning={"effort": "medium"},
        text={"format": {"type": "text"}},
        tool_choice={"type": "auto"},
        tools=[{"type": "function", "name": "lookup"}],
        truncation="auto",
    )

    assert request.to_payload() == {
        "conversation": {"id": "conv_123"},
        "instructions": "You are terse.",
        "model": "gpt-5-mini",
        "parallel_tool_calls": True,
        "previous_response_id": "resp_123",
        "reasoning": {"effort": "medium"},
        "text": {"format": {"type": "text"}},
        "tool_choice": {"type": "auto"},
        "tools": [{"type": "function", "name": "lookup"}],
        "truncation": "auto",
    }


def test_openai_request_omits_input_when_not_provided() -> None:
    """The request model should allow conversation-only count payloads."""

    request = OpenAICountTokensRequest(
        model="gpt-5-mini",
        previous_response_id="resp_123",
    )

    assert request.to_payload() == {
        "model": "gpt-5-mini",
        "previous_response_id": "resp_123",
    }


@pytest.mark.parametrize(
    ("request_kwargs", "message"),
    [
        ({"model": 1}, "model must be a string"),
        ({"model": "gpt-5-mini", "input": 1}, "input must be a string, a list, or None"),
        (
            {"model": "gpt-5-mini", "input": ["hello"]},
            "input lists must contain dictionaries",
        ),
        (
            {"model": "gpt-5-mini", "conversation": 1},
            "conversation must be a string, a dictionary, or None",
        ),
        (
            {"model": "gpt-5-mini", "instructions": 1},
            "instructions must be a string or None",
        ),
        (
            {"model": "gpt-5-mini", "parallel_tool_calls": "yes"},
            "parallel_tool_calls must be a boolean or None",
        ),
        (
            {"model": "gpt-5-mini", "previous_response_id": 1},
            "previous_response_id must be a string or None",
        ),
        (
            {"model": "gpt-5-mini", "reasoning": "medium"},
            "reasoning must be a dictionary or None",
        ),
        ({"model": "gpt-5-mini", "text": "plain"}, "text must be a dictionary or None"),
        (
            {"model": "gpt-5-mini", "tool_choice": 1},
            "tool_choice must be a string, a dictionary, or None",
        ),
        (
            {"model": "gpt-5-mini", "tools": {"type": "function"}},
            "tools must be a list or None",
        ),
        (
            {"model": "gpt-5-mini", "tools": ["lookup"]},
            "tools must contain dictionaries",
        ),
        (
            {"model": "gpt-5-mini", "truncation": "enabled"},
            "truncation must be 'auto', 'disabled', or None",
        ),
    ],
)
def test_openai_request_rejects_invalid_field_types(
    request_kwargs: dict[str, t.Any],
    message: str,
) -> None:
    """The request model should validate supported top-level field types."""

    with pytest.raises(TypeError, match=message):
        OpenAICountTokensRequest(**request_kwargs)


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
        assert request == OpenAICountTokensRequest(
            model="gpt-5-mini",
            input=[
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": "hello"}],
                }
            ],
            previous_response_id="resp_123",
            tools=[{"type": "function", "name": "lookup"}],
        )
        return 18

    monkeypatch.setattr(OpenAIProvider, "count_tokens", fake_count_tokens)

    token_count = TokenCount.from_openai(
        model="gpt-5-mini",
        api_key="secret",
        input=[
            {
                "role": "user",
                "content": [{"type": "input_text", "text": "hello"}],
            }
        ],
        previous_response_id="resp_123",
        tools=[{"type": "function", "name": "lookup"}],
    )

    assert token_count == TokenCount(total=18)
