# API Module

`src/kentokit/api.py` is the public entry point for token counting. It keeps the package surface small by exposing one function, `calc_tokens`, plus the normalized `TokenCount` return model, and delegates provider-specific behavior to the provider registry.

## Responsibilities

- Accept the public inputs required to count tokens: plain-text `input_data` plus `model_ref`, or an `OpenAICountTokensRequest` when `provider_id="openai"`, together with `provider_id` and `api_key`.
- Resolve the provider implementation from the registry in `kentokit.providers`.
- Instantiate the provider, collect the integer token count, and return a `TokenCount`.
- Reject unsupported providers before any network request is made.

## Public surface

The module exposes one public function and works with two public models:

- `calc_tokens(...) -> TokenCount`: dispatch plain-text requests to any provider and dispatch `OpenAICountTokensRequest` only to OpenAI.
- `TokenCount(total: int)`: normalized response model for the public API. It also exposes `TokenCount.from_openai(...)` for the typed OpenAI path.
- `OpenAICountTokensRequest(model: str, input: str)`: validated OpenAI request model used by the OpenAI-specific typed paths.

The module also contains one internal helper:

- `_get_provider_class(...) -> type[ProviderBase]`: lookup wrapper around `PROVIDER_REGISTRY` that raises `UnsupportedProviderError` for unknown provider identifiers.

## Request flow

```mermaid
flowchart LR
    A["Caller"] --> B["calc_tokens(...)"]
    B --> C{"OpenAI request object?"}
    C -->|No| D["_get_provider_class(provider_id)"]
    D --> E["PROVIDER_REGISTRY"]
    E --> F["provider = ProviderClass(api_key=...)"]
    F --> G["provider.count_tokens(input_data, model_ref)"]
    G --> H["Provider HTTP request + response parsing"]
    H --> I["int token count"]
    I --> J["TokenCount(total=...)"]
    C -->|Yes| K["OpenAIProvider(api_key=...)"]
    K --> L["provider.count_tokens(request=...)"]
    L --> H
```

## Module dependencies

- `kentokit.openai.OpenAICountTokensRequest`: validated OpenAI request abstraction for the typed OpenAI path.
- `kentokit.providers.PROVIDER_REGISTRY`: source of truth for supported providers.
- `kentokit.providers.base.ProviderBase`: base type returned by the registry.
- `kentokit.providers.base.ProviderId`: supported provider identifier literal type.
- `kentokit.providers.base.UnsupportedProviderError`: raised when the provider id is not registered.
- `kentokit.providers.openai.OpenAIProvider`: OpenAI transport used by the request-object path and `TokenCount.from_openai(...)`.

## Error model

`calc_tokens` can fail in two distinct ways:

- `UnsupportedProviderError`: the caller passed a provider id that is not registered.
- `TokenCountError`: the resolved provider failed to make the request, decode the response, or extract the expected token count.
- `TypeError`: the caller passed an `OpenAICountTokensRequest` with a non-OpenAI provider id, or mixed a request object with `model_ref`.

The API module does not catch and translate provider failures. It lets provider-layer errors propagate so callers can inspect the provider id, HTTP status code, and response text carried by `TokenCountError`.

## Design notes

- The API layer does not know provider-specific URLs, headers, or payload shapes.
- Provider instances are created per call with only the API key as constructor state.
- `calc_tokens` remains provider-agnostic for plain-text requests, with one narrow overload for the OpenAI request model.
- Adding a new provider should not require changing `calc_tokens`; only the registry and provider implementation need to change, unless a future provider also gets a typed request model.
