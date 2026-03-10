"""Gemini token counting example."""

import os

from dotenv import load_dotenv

from kentokit import TokenCount


def main() -> None:
    """Run the Gemini token counting example."""

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key is None:
        raise RuntimeError("Missing GEMINI_API_KEY in the environment or .env file.")

    token_count = TokenCount.from_gemini(
        model="gemini-2.0-flash",
        api_key=api_key,
        contents=[
            {
                "role": "user",
                "parts": [{"text": "Count the tokens in this Gemini example."}],
            }
        ],
    )
    print(f"Gemini token count: {token_count.total}")


if __name__ == "__main__":
    main()
