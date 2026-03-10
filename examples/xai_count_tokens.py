"""xAI token counting example."""

import os

from dotenv import load_dotenv

from kentokit import TokenCount


def main() -> None:
    """Run the xAI token counting example."""

    load_dotenv()
    api_key = os.getenv("XAI_API_KEY")
    if api_key is None:
        raise RuntimeError("Missing XAI_API_KEY in the environment or .env file.")

    token_count = TokenCount.from_xai(
        model="grok-4-fast",
        text="Count the tokens in this xAI example.",
        api_key=api_key,
    )
    print(f"xAI token count: {token_count.total}")


if __name__ == "__main__":
    main()
