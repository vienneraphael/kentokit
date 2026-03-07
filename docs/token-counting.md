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

## Supported Providers

- `openai`
- `anthropic`
- `gemini`
- `xai`

## Example

```python
from kentokit import calc_tokens

token_count = calc_tokens(
    input_data="Count my tokens.",
    model_ref="gpt-5-mini",
    provider_id="openai",
    api_key="example-api-key",  # pragma: allowlist secret
)
print(token_count)
```

Output:

```text
15
```
