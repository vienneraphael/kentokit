# AGENTS.md

## Repository Expectations

- use ripgrep (through `rg` command) in place of grep.
- Document public utilities in `docs/` when you change behavior.
- Whenever you import typing, use: `import typing as t`
- Use as much typing as possible on your function definitions
- Use python native type hinting whenever possible, e.g. `list[dict]`
- Always use named-arguments when calling functions or methods.
- Document function and methods using numpy-style docs.
- To install libraries to the project, use `uv add`

## Development workflows

- When asking me questions in Plan Mode, give me extensive information to make an informed choice: define the impact of each invidual choice and give context about the question before asking it.

- Run tests (using pytest) for every code change but not when changing code comments or documentation-related stuff.
If the pytest command does not work due to missing imports, try activating the environment first with `source .venv/bin/activate`
- Run pre-commits (using `prek run -a`) for every code change including code comments or documentation.

pre-commits to check for:

- pre-commit-hooks/ruff-check/ruff-format: syntax/style related, they autofix most of the time
- markdownlint-cli: syntax/style related, does not autofix.
- ty-check: type hinting, does not autofix
- bandit/detect-secrets: security-related, does not autofix but can have false flags.

- When updating static docs, always rebuild in strict mode after your changes. In that case, no need to run tests with pytest.

- When pursuing a complex task, break it down as simpler tasks and make atomic commits to facilitate code review.
Do the atomic commits yourself using `git commit -m`.
When the task is done, include atomic commit names in your recap to streamline your approach.
Always follow good practices for atomic commits.

## Component index

- `docs/architecture/api.md`: architecture note for the public token counting entry point in `src/kentokit/api.py`, including responsibilities, request flow, dependencies, and error boundaries.
- `docs/architecture/providers.md`: architecture note for `src/kentokit/providers/`, covering the provider registry, `ProviderBase`, concrete providers, and the extension path for adding new providers.

## End-to-end flow (high level)

- Treat `src/kentokit/api.py` as the API gateway for token counting: callers enter either through `calc_tokens(...)` or provider-specific helpers such as `TokenCount.from_openai(...)`.
- The public entrypoint resolves the provider implementation from `kentokit.providers.PROVIDER_REGISTRY` and routes the request to the matching provider adapter.
- The API layer accepts either a simple raw string input or a provider-native request shape for the selected provider.
- Before any HTTP request is sent, the provider adapter validates the input into a provider-native typed request model owned by `kentokit`.
- The validated provider-native request model is serialized into the upstream JSON payload as-is, without first forcing it through a cross-provider lowest-common-denominator schema.
- The provider adapter builds the upstream request details for its vendor: URL, headers, and JSON payload.
- The shared provider execution flow sends the request, normalizes transport and decoding failures into `TokenCountError`, and hands the parsed JSON body back to the concrete provider.
- The concrete provider extracts the vendor-specific count and returns normalized data to the shared layer.
- The shared layer builds the final `TokenCount` result returned to the caller.

## Overall Coding Principles

Whenever asked to do something, strictly follow these principles in your actions.

### 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:

- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:

- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:

- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

---

### Anti-Patterns Summary

| Principle | Anti-Pattern | Fix |
| ----------- | ------------- | ----- |
| Think Before Coding | Silently assumes file format, fields, scope | List assumptions explicitly, ask for clarification |
| implicity First | Strategy pattern for single discount calculation | One function until complexity is actually needed |
| Surgical Changes | Reformats quotes, adds type hints while fixing bug | Only change lines that fix the reported issue |
| Goal-Driven | "I'll review and improve the code" | "Write test for bug X → make it pass → verify no regressions" |

### Key Insight

The "overcomplicated" examples aren't obviously wrong—they follow design patterns and best practices. The problem iming**: they add complexity before it's needed, which:

- Makes code harder to understand
- Introduces more bugs
- Takes longer to implement
- Harder to test

The "simple" versions are:

- Easier to understand
- Faster to implement
- Easier to test
- Can be refactored later when complexity is actually needed

**Good code is code that solves today's problem simply, not tomorrow's problem prematurely.**
