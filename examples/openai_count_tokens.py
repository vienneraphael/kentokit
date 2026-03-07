"""OpenAI token counting example."""

import os

from dotenv import load_dotenv

from kentokit import calc_tokens


def main() -> None:
    """Run the OpenAI token counting example."""

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key is None:
        raise RuntimeError("Missing OPENAI_API_KEY in the environment or .env file.")

    token_count = calc_tokens(
        input_data="Count the tokens in this OpenAI example.",
        model_ref="gpt-5-mini",
        provider_id="openai",
        api_key=api_key,
    )
    print(f"OpenAI token count: {token_count}")


if __name__ == "__main__":
    main()
