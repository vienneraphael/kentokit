"""Gemini token count provider."""

import typing as t
from urllib.parse import quote

from kentokit.providers.base import ProviderBase, TokenCountError


class GeminiProvider(ProviderBase):
    """Gemini token counting implementation."""

    provider_id = "gemini"

    def build_url(self, *, model_ref: str) -> str:
        """Build the Gemini token count URL.

        Parameters
        ----------
        model_ref : str
            Gemini model identifier.

        Returns
        -------
        str
            Gemini token count endpoint.
        """

        normalized_model_ref = self.normalize_model_ref(model_ref=model_ref)
        return (
            "https://generativelanguage.googleapis.com/v1beta/"
            f"{quote(normalized_model_ref, safe='/')}:countTokens?key={quote(self.api_key)}"
        )

    def build_payload(self, *, input_data: str, model_ref: str) -> dict[str, t.Any]:
        """Build the Gemini JSON payload.

        Parameters
        ----------
        input_data : str
            Plain text input to count.
        model_ref : str
            Gemini model identifier.

        Returns
        -------
        dict[str, Any]
            Gemini JSON payload.
        """

        return {
            "contents": [
                {
                    "parts": [{"text": input_data}],
                    "role": "user",
                }
            ]
        }

    def parse_token_count(self, *, data: dict[str, t.Any]) -> int:
        """Parse the Gemini token count response.

        Parameters
        ----------
        data : dict[str, Any]
            Gemini response body.

        Returns
        -------
        int
            Parsed token count.
        """

        total_tokens = data.get("totalTokens")
        if not isinstance(total_tokens, int):
            raise TokenCountError(
                provider_id=self.provider_id,
                message="expected integer field 'totalTokens'",
            )
        return total_tokens

    @staticmethod
    def normalize_model_ref(*, model_ref: str) -> str:
        """Normalize Gemini model references.

        Parameters
        ----------
        model_ref : str
            Gemini model identifier.

        Returns
        -------
        str
            Gemini model identifier prefixed with ``models/`` when needed.
        """

        if model_ref.startswith("models/"):
            return model_ref
        return f"models/{model_ref}"
