"""Gemini token counting example."""

import os

from dotenv import load_dotenv

from kentokit import calc_tokens


def main() -> None:
    """Run the Gemini token counting example."""

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key is None:
        raise RuntimeError("Missing GEMINI_API_KEY in the environment or .env file.")

    token_count = calc_tokens(
        input_data="Count the tokens in this Gemini example.",
        model_ref="gemini-2.0-flash",
        provider_id="gemini",
        api_key=api_key,
    )
    print(f"Gemini token count: {token_count}")


if __name__ == "__main__":
    main()
