"""Count tokens with Amazon Bedrock."""

from kentokit import BedrockCountTokensRequest, calc_tokens

request = BedrockCountTokensRequest(
    model="anthropic.claude-3-5-haiku-20241022-v1:0",
    region="us-west-2",
    converse={
        "messages": [
            {
                "role": "user",
                "content": [{"text": "Count my tokens."}],
            }
        ]
    },
)

# Bedrock token counting is typed-request-only; plain string input is not supported.
token_count = calc_tokens(
    input_data=request,
    provider_id="bedrock",
    api_key="example-api-key",  # pragma: allowlist secret
)

print(token_count.total)
