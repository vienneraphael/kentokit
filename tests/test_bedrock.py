"""Tests for Bedrock-specific request helpers."""

import json
import typing as t

import httpx
import pytest

from kentokit import BedrockCountTokensRequest, TokenCount
from kentokit.providers.bedrock import BedrockProvider


def test_bedrock_request_serializes_converse_to_payload() -> None:
    """The request model should serialize Bedrock converse payloads."""

    request = BedrockCountTokensRequest(
        model="anthropic.claude-3-5-haiku-20241022-v1:0",
        region="us-west-2",
        converse={"messages": [{"role": "user", "content": [{"text": "hello"}]}]},
    )

    assert request.to_payload() == {
        "input": {
            "converse": {
                "messages": [{"role": "user", "content": [{"text": "hello"}]}],
            }
        }
    }


def test_bedrock_request_serializes_invoke_model_string_to_payload() -> None:
    """The request model should preserve invokeModel JSON strings."""

    request = BedrockCountTokensRequest(
        model="anthropic.claude-3-5-haiku-20241022-v1:0",
        region="us-west-2",
        invoke_model_body='{"messages":[{"role":"user","content":"hello"}]}',
    )

    assert request.to_payload() == {
        "input": {
            "invokeModel": {
                "body": '{"messages":[{"role":"user","content":"hello"}]}',
            }
        }
    }


def test_bedrock_request_serializes_invoke_model_dict_to_payload() -> None:
    """The request model should JSON-serialize invokeModel dictionaries."""

    request = BedrockCountTokensRequest(
        model="anthropic.claude-3-5-haiku-20241022-v1:0",
        region="us-west-2",
        invoke_model_body={
            "messages": [{"role": "user", "content": "hello"}],
        },
    )

    assert request.to_payload() == {
        "input": {
            "invokeModel": {
                "body": json.dumps({"messages": [{"role": "user", "content": "hello"}]}),
            }
        }
    }


def test_token_count_from_bedrock_uses_request_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The classmethod should route a validated request through BedrockProvider."""

    def fake_count_tokens(
        self: BedrockProvider,
        *,
        request: BedrockCountTokensRequest,
        client: httpx.Client | None = None,
        input_data: str | None = None,
        model_ref: str | None = None,
    ) -> int:
        del client, input_data, model_ref
        assert self.api_key == "secret"
        assert request == BedrockCountTokensRequest(
            model="anthropic.claude-3-5-haiku-20241022-v1:0",
            region="us-west-2",
            converse={"messages": [{"role": "user", "content": [{"text": "hello"}]}]},
        )
        return 19

    monkeypatch.setattr(BedrockProvider, "count_tokens", fake_count_tokens)

    token_count = TokenCount.from_bedrock(
        model="anthropic.claude-3-5-haiku-20241022-v1:0",
        region="us-west-2",
        api_key="secret",
        converse={"messages": [{"role": "user", "content": [{"text": "hello"}]}]},
    )

    assert token_count == TokenCount(total=19)


@pytest.mark.parametrize(
    ("request_kwargs", "message"),
    [
        (
            {
                "model": 1,
                "region": "us-west-2",
                "converse": {"messages": []},
            },
            "model must be a string",
        ),
        (
            {
                "model": "anthropic.claude-3-5-haiku-20241022-v1:0",
                "region": 1,
                "converse": {"messages": []},
            },
            "region must be a string",
        ),
        (
            {
                "model": "anthropic.claude-3-5-haiku-20241022-v1:0",
                "region": "us-west-2",
                "converse": "hello",
            },
            "converse must be a dictionary or None",
        ),
        (
            {
                "model": "anthropic.claude-3-5-haiku-20241022-v1:0",
                "region": "us-west-2",
                "invoke_model_body": 1,
            },
            "invoke_model_body must be a string, a dictionary, or None",
        ),
        (
            {
                "model": "anthropic.claude-3-5-haiku-20241022-v1:0",
                "region": "us-west-2",
            },
            "exactly one of converse or invoke_model_body must be provided",
        ),
        (
            {
                "model": "anthropic.claude-3-5-haiku-20241022-v1:0",
                "region": "us-west-2",
                "converse": {"messages": []},
                "invoke_model_body": "{}",
            },
            "exactly one of converse or invoke_model_body must be provided",
        ),
    ],
)
def test_bedrock_request_rejects_invalid_fields(
    request_kwargs: dict[str, t.Any],
    message: str,
) -> None:
    """The request model should validate Bedrock top-level field types."""

    with pytest.raises(TypeError, match=message):
        BedrockCountTokensRequest(**request_kwargs)
