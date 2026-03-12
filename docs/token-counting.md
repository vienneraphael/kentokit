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

::: kentokit.modalities.GeminiModality
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

Gemini responses can also populate Gemini-specific metadata on `TokenCount`:

- `cached_tokens`: cached-token total returned by Gemini, when present
- `token_details`: prompt-side modality breakdown
- `cache_token_details`: cache-side modality breakdown

Each breakdown is a dictionary from `GeminiModality` to `int`.

Example:

```python
from kentokit import GeminiModality, TokenCount

token_count = TokenCount(
    total=17,
    cached_tokens=5,
    token_details={
        GeminiModality.TEXT: 12,
        GeminiModality.IMAGE: 5,
    },
    cache_token_details={
        GeminiModality.TEXT: 5,
    },
)

assert token_count.cached_tokens == 5
assert token_count.token_details[GeminiModality.TEXT] == 12
```

## OpenAI Typed Request

```python
from kentokit import OpenAICountTokensRequest, TokenCount, calc_tokens

request = OpenAICountTokensRequest(
    model="gpt-5-mini",
    input=[
        {
            "role": "user",
            "content": [{"type": "input_text", "text": "Count my tokens."}],
        }
    ],
    tools=[{"type": "function", "name": "lookup"}],
)

typed_token_count = TokenCount.from_openai(
    model="gpt-5-mini",
    api_key="example-api-key",  # pragma: allowlist secret
    input=[
        {
            "role": "user",
            "content": [{"type": "input_text", "text": "Count my tokens."}],
        }
    ],
    tools=[{"type": "function", "name": "lookup"}],
)

overloaded_token_count = calc_tokens(
    input_data=request,
    provider_id="openai",
    api_key="example-api-key",  # pragma: allowlist secret
)

assert typed_token_count.total == overloaded_token_count.total
```

OpenAI count requests can also reuse conversation state without sending a fresh
`input` payload:

```python
from kentokit import OpenAICountTokensRequest, TokenCount

request = OpenAICountTokensRequest(
    model="gpt-5-mini",
    previous_response_id="resp_123",
    conversation="conv_123",
)

token_count = TokenCount.from_openai(
    model="gpt-5-mini",
    api_key="example-api-key",  # pragma: allowlist secret
    previous_response_id="resp_123",
    conversation="conv_123",
)

assert isinstance(request.to_payload(), dict)
assert token_count.total >= 0
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

Additional Gemini multimodal examples are available in:

- `examples/gemini/count_tokens.py`
- `examples/gemini/count_tokens_inline_image.py`
- `examples/gemini/count_tokens_video.py`
- `examples/gemini/count_tokens_pdf.py`

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
