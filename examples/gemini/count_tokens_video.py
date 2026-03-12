"""Gemini video token counting example."""

from _helpers import build_inline_media_part, load_gemini_api_key, print_token_count

from kentokit import TokenCount

PROMPT = "Tell me about this video."
BIG_BUCK_BUNNY_VIDEO_URL = (
    "https://raw.githubusercontent.com/bower-media-samples/big-buck-bunny-480p-30s/master/video.mp4"
)


def main() -> None:
    """Run the Gemini video token counting example."""

    api_key = load_gemini_api_key()
    video_part = build_inline_media_part(
        url=BIG_BUCK_BUNNY_VIDEO_URL,
        mime_type="video/mp4",
    )
    token_count = TokenCount.from_gemini(
        model="gemini-2.0-flash",
        api_key=api_key,
        contents=[
            {
                "role": "user",
                "parts": [
                    {"text": PROMPT},
                    video_part,
                ],
            }
        ],
    )
    print_token_count(label="Video", token_count=token_count)


if __name__ == "__main__":
    main()
