"""Anthropic token counting example."""

import os

from dotenv import load_dotenv

from kentokit import calc_tokens


def main() -> None:
    """Run the Anthropic token counting example."""

    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key is None:
        raise RuntimeError("Missing ANTHROPIC_API_KEY in the environment or .env file.")

    token_count = calc_tokens(
        input_data="Count the tokens in this Anthropic example.",
        model_ref="claude-sonnet-4-5",
        provider_id="anthropic",
        api_key=api_key,
    )
    print(f"Anthropic token count: {token_count}")


if __name__ == "__main__":
    main()
