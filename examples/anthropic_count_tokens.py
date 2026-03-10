"""Anthropic token counting example."""

import os

from dotenv import load_dotenv

from kentokit import TokenCount


def main() -> None:
    """Run the Anthropic token counting example."""

    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key is None:
        raise RuntimeError("Missing ANTHROPIC_API_KEY in the environment or .env file.")

    token_count = TokenCount.from_anthropic(
        model="claude-sonnet-4-5",
        messages=[
            {
                "role": "user",
                "content": "Count the tokens in this Anthropic example.",
            }
        ],
        api_key=api_key,
    )
    print(f"Anthropic token count: {token_count.total}")


if __name__ == "__main__":
    main()
