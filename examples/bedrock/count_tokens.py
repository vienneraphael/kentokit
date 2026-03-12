"""Bedrock token counting example."""

import os

from dotenv import load_dotenv

from kentokit import TokenCount


def main() -> None:
    """Run the Bedrock token counting example."""

    load_dotenv()
    api_key = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
    if api_key is None:
        raise RuntimeError("Missing AWS_BEARER_TOKEN_BEDROCK in the environment or .env file.")

    token_count = TokenCount.from_bedrock(
        model="anthropic.claude-3-5-haiku-20241022-v1:0",
        region="us-west-2",
        api_key=api_key,
        converse={
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": "Count the tokens in this Bedrock example."}],
                }
            ]
        },
    )
    print(f"Bedrock token count: {token_count.total}")


if __name__ == "__main__":
    main()
