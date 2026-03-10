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

::: kentokit.requests.anthropic.AnthropicCountTokensRequest
    options:
      separate_signature: true
      show_root_heading: true
      show_root_full_path: false
      show_source: true
      heading_level: 2
      docstring_style: numpy

::: kentokit.requests.openai.OpenAICountTokensRequest
    options:
      separate_signature: true
      show_root_heading: true
      show_root_full_path: false
      show_source: true
      heading_level: 2
      docstring_style: numpy

::: kentokit.requests.gemini.GeminiCountTokensRequest
    options:
      separate_signature: true
      show_root_heading: true
      show_root_full_path: false
      show_source: true
      heading_level: 2
      docstring_style: numpy

::: kentokit.requests.xai.XAICountTokensRequest
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

## Anthropic Typed Request

```python
from kentokit import AnthropicCountTokensRequest, TokenCount, calc_tokens

request = AnthropicCountTokensRequest(
    model="claude-sonnet-4-5",
    messages=[{"role": "user", "content": "Count my tokens."}],
    system="You are terse.",
)

typed_token_count = TokenCount.from_anthropic(
    model="claude-sonnet-4-5",
    messages=[{"role": "user", "content": "Count my tokens."}],
    api_key="example-api-key",  # pragma: allowlist secret
    system="You are terse.",
)

overloaded_token_count = calc_tokens(
    input_data=request,
    provider_id="anthropic",
    api_key="example-api-key",  # pragma: allowlist secret
)

assert typed_token_count.total == overloaded_token_count.total
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

## Gemini Typed Request

```python
from kentokit import GeminiCountTokensRequest, TokenCount, calc_tokens

request = GeminiCountTokensRequest(
    model="gemini-2.0-flash",
    contents=[{"role": "user", "parts": [{"text": "Count my tokens."}]}],
)

typed_token_count = TokenCount.from_gemini(
    model="gemini-2.0-flash",
    api_key="example-api-key",  # pragma: allowlist secret
    contents=[{"role": "user", "parts": [{"text": "Count my tokens."}]}],
)

overloaded_token_count = calc_tokens(
    input_data=request,
    provider_id="gemini",
    api_key="example-api-key",  # pragma: allowlist secret
)

assert typed_token_count.total == overloaded_token_count.total
```

## xAI Typed Request

```python
from kentokit import TokenCount, XAICountTokensRequest, calc_tokens

request = XAICountTokensRequest(
    model="grok-4-fast",
    text="Count my tokens.",
)

typed_token_count = TokenCount.from_xai(
    model="grok-4-fast",
    text="Count my tokens.",
    api_key="example-api-key",  # pragma: allowlist secret
)

overloaded_token_count = calc_tokens(
    input_data=request,
    provider_id="xai",
    api_key="example-api-key",  # pragma: allowlist secret
)

assert typed_token_count.total == overloaded_token_count.total
```
