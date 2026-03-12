"""Helpers shared by Gemini token-counting examples."""

import base64
import os
import typing as t

import httpx
from dotenv import load_dotenv

DOWNLOAD_HEADERS = {
    "Accept": "*/*",
    "User-Agent": "kentokit-example/1.0",
}


def load_gemini_api_key() -> str:
    """Load the Gemini API key from the environment.

    Returns
    -------
    str
        Gemini API key.

    Raises
    ------
    RuntimeError
        If ``GEMINI_API_KEY`` is not available.
    """

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key is None:
        raise RuntimeError("Missing GEMINI_API_KEY in the environment or .env file.")
    return api_key


def download_media_bytes(*, url: str) -> bytes:
    """Download a public media file used by an example.

    Parameters
    ----------
    url : str
        Public URL for the sample media file.

    Returns
    -------
    bytes
        Downloaded file contents.
    """

    response = httpx.get(
        url=url,
        follow_redirects=True,
        headers=DOWNLOAD_HEADERS,
        timeout=30.0,
    )
    response.raise_for_status()
    return response.content


def build_inline_media_part(
    *,
    url: str,
    mime_type: str,
) -> dict[str, dict[str, str]]:
    """Build an inline Gemini media part from a public URL.

    Parameters
    ----------
    url : str
        Public URL for the media file.
    mime_type : str
        MIME type sent to Gemini.

    Returns
    -------
    dict[str, dict[str, str]]
        Gemini ``inlineData`` part.
    """

    media_bytes = download_media_bytes(url=url)
    encoded_bytes = base64.b64encode(media_bytes).decode("ascii")
    return {
        "inlineData": {
            "mimeType": mime_type,
            "data": encoded_bytes,
        }
    }


def print_token_count(*, label: str, token_count: t.Any) -> None:
    """Print the normalized token count and optional Gemini metadata.

    Parameters
    ----------
    label : str
        Human-readable example label.
    token_count : Any
        Token count object returned by ``kentokit``.
    """

    print(f"{label} total tokens: {token_count.total}")
    print(f"{label} cached tokens: {token_count.cached_tokens}")
    print(f"{label} token details: {token_count.token_details}")
    print(f"{label} cache token details: {token_count.cache_token_details}")
