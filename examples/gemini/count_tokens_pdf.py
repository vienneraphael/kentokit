"""Gemini PDF token counting example."""

from _helpers import build_inline_media_part, load_gemini_api_key, print_token_count

from kentokit import TokenCount

PROMPT = "Give me a summary of this document."
SAMPLE_PDF_URL = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"


def main() -> None:
    """Run the Gemini PDF token counting example."""

    api_key = load_gemini_api_key()
    pdf_part = build_inline_media_part(
        url=SAMPLE_PDF_URL,
        mime_type="application/pdf",
    )
    token_count = TokenCount.from_gemini(
        model="gemini-2.0-flash",
        api_key=api_key,
        contents=[
            {
                "role": "user",
                "parts": [
                    {"text": PROMPT},
                    pdf_part,
                ],
            }
        ],
    )
    print_token_count(label="PDF", token_count=token_count)


if __name__ == "__main__":
    main()
