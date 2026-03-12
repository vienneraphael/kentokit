"""Gemini inline-image token counting example."""

from _helpers import build_inline_media_part, load_gemini_api_key, print_token_count

from kentokit import TokenCount

PROMPT = "Tell me about this image."
MONA_LISA_IMAGE_URL = "https://upload.wikimedia.org/wikipedia/commons/6/6a/Mona_Lisa.jpg"


def main() -> None:
    """Run the Gemini inline-image token counting example."""

    api_key = load_gemini_api_key()
    image_part = build_inline_media_part(
        url=MONA_LISA_IMAGE_URL,
        mime_type="image/jpeg",
    )
    token_count = TokenCount.from_gemini(
        model="gemini-2.0-flash",
        api_key=api_key,
        contents=[
            {
                "role": "user",
                "parts": [
                    {"text": PROMPT},
                    image_part,
                ],
            }
        ],
    )
    print_token_count(label="Inline image", token_count=token_count)


if __name__ == "__main__":
    main()
