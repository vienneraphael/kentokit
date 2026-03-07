"""xAI token counting example."""

import os

from dotenv import load_dotenv

from kentokit import calc_tokens


def main() -> None:
    """Run the xAI token counting example."""

    load_dotenv()
    api_key = os.getenv("XAI_API_KEY")
    if api_key is None:
        raise RuntimeError("Missing XAI_API_KEY in the environment or .env file.")

    token_count = calc_tokens(
        input_data="Count the tokens in this xAI example.",
        model_ref="grok-4-fast",
        provider_id="xai",
        api_key=api_key,
    )
    print(f"xAI token count: {token_count}")


if __name__ == "__main__":
    main()
