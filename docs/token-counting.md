---
title: Token Counting
---

`kentokit` exposes a small synchronous helper for counting text tokens through
provider HTTP APIs.

## Public API

::: kentokit.api

## Supported Providers

- `openai`
- `anthropic`
- `gemini`
- `xai`

## Scope

- `input_data` must be a plain `str`
- the return value is an `int`
- the abstraction only covers provider token counting/tokenize endpoints

## Example

```python
from kentokit import calc_tokens

token_count = calc_tokens(
    input_data="Count my tokens.",
    model_ref="gpt-5-mini",
    provider_id="openai",
    api_key="example-api-key",  # pragma: allowlist secret
)
```
