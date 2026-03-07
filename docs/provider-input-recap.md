---
title: Provider Input Recap
---

This page summarizes what the current `kentokit` provider implementations can
count in the request input.

Scope note: this is based on the payloads implemented in
`src/kentokit/providers/`. It does not try to describe every object the
upstream vendor APIs may support outside the current library surface.

## Baseline Constraint

All four providers currently receive `input_data: str` through
`ProviderBase.count_tokens(...)`, so `kentokit` only exposes one caller-facing
countable input type today: a single plain text string.

## Provider Mapping

| Provider | Implemented countable input shape | Implemented request fragment |
| --- | --- | --- |
| OpenAI | One plain text string | `{"input": "<text>", "model": "<model>"}` |
| Anthropic | One user message whose content is one plain text string | `{"messages": [{"role": "user", "content": "<text>"}], "model": "<model>"}` |
| Gemini | One user content object containing one text part | `{"contents": [{"role": "user", "parts": [{"text": "<text>"}]}]}` |
| xAI | One plain text string | `{"model": "<model>", "text": "<text>"}` |

## Common Objects

The following countable objects are shared by all four implemented providers:

- Plain text string.
  Every provider ultimately counts tokens from the same single text value passed
  as `input_data`.

## Specific Objects

These objects are provider-specific beyond the common plain text string, sorted
by the number of implemented providers that allow them.

### Supported by 2 providers

- User-role wrapper object.
  Anthropic and Gemini both wrap the counted text in an object with
  `role="user"`.

- Single-item top-level collection of user input objects.
  Anthropic uses `messages=[...]` and Gemini uses `contents=[...]`.

## Supported by 1 provider

- OpenAI: bare `input` field.
  OpenAI is the only implemented provider that sends the counted text directly
  as `input`.

- Anthropic: message object with `content`.
  Anthropic is the only implemented provider that sends the counted text as a
  message object shaped like `{"role": "user", "content": "<text>"}`.

- Gemini: content object with nested `parts`.
  Gemini is the only implemented provider that sends the counted text through
  `contents[].parts[].text`.

- xAI: bare `text` field.
  xAI is the only implemented provider that sends the counted text directly as
  `text`.

## Practical Reading

If you compare only what `kentokit` can submit today, the overlap is narrow:

- Shared across all providers: one plain text string.
- Shared across a subset: a user-scoped wrapper plus a one-item collection
  wrapper in Anthropic and Gemini.
- Unique to one provider each: the exact envelope used to hold that string.
