---
title: Token Counting
---

`kentokit` exposes a small synchronous helper for counting text tokens through
provider HTTP APIs.

::: kentokit.api.calc_tokens
    options:
      separate_signature: true
      show_root_heading: true
      show_root_full_path: false
      show_source: true
      heading_level: 2
      docstring_style: numpy

::: kentokit.token_count.TokenCount
    options:
      separate_signature: true
      show_root_heading: true
      show_root_full_path: false
      show_source: true
      heading_level: 2
      docstring_style: numpy

::: kentokit.openai.OpenAICountTokensRequest
    options:
      separate_signature: true
      show_root_heading: true
      show_root_full_path: false
      show_source: true
      heading_level: 2
      docstring_style: numpy

## Supported Providers

- `openai`
- `anthropic`
- `gemini`
- `xai`

## Example

```python
from kentokit import TokenCount, calc_tokens

token_count = calc_tokens(
    input_data="Count my tokens.",
    model_ref="gpt-5-mini",
    provider_id="openai",
    api_key="example-api-key",  # pragma: allowlist secret
)
assert isinstance(token_count, TokenCount)
print(token_count.total)
```

Output:

```text
15
```

## OpenAI Typed Request

```python
from kentokit import OpenAICountTokensRequest, TokenCount, calc_tokens

request = OpenAICountTokensRequest(
    model="gpt-5-mini",
    input="Count my tokens.",
)

typed_token_count = TokenCount.from_openai(
    model="gpt-5-mini",
    input="Count my tokens.",
    api_key="example-api-key",  # pragma: allowlist secret
)

overloaded_token_count = calc_tokens(
    input_data=request,
    provider_id="openai",
    api_key="example-api-key",  # pragma: allowlist secret
)

assert typed_token_count.total == overloaded_token_count.total
```
