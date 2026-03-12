# kentokit

Synchronous token counting helpers for multiple model providers.

## Supported providers

- `openai`
- `anthropic`
- `bedrock`
- `gemini`
- `xai`

## Bedrock example

Bedrock token counting is typed-request-only because the upstream API accepts
provider-native request unions instead of a generic raw text body.

```python
from kentokit import BedrockCountTokensRequest, TokenCount, calc_tokens

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

token_count = calc_tokens(
    input_data=request,
    provider_id="bedrock",
    api_key="example-api-key",  # pragma: allowlist secret
)

assert isinstance(token_count, TokenCount)
```
