"""OpenAI token counting example."""

import os

from dotenv import load_dotenv

from kentokit import TokenCount


def main() -> None:
    """Run the OpenAI token counting example."""

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key is None:
        raise RuntimeError("Missing OPENAI_API_KEY in the environment or .env file.")

    token_count = TokenCount.from_openai(
        model="gpt-5-mini",
        input="Count the tokens in this OpenAI example.",
        api_key=api_key,
    )
    print(f"OpenAI token count: {token_count.total}")


if __name__ == "__main__":
    main()
