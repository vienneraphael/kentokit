"""Anthropic token count provider."""

import typing as t

from kentokit.providers.base import ProviderBase, TokenCountError


class AnthropicProvider(ProviderBase):
    """Anthropic token counting implementation."""

    provider_id = "anthropic"

    def build_url(self, *, model_ref: str) -> str:
        """Build the Anthropic token count URL.

        Parameters
        ----------
        model_ref : str
            Anthropic model identifier.

        Returns
        -------
        str
            Anthropic token count endpoint.
        """

        return "https://api.anthropic.com/v1/messages/count_tokens"

    def build_headers(self) -> dict[str, str]:
        """Build Anthropic request headers.

        Returns
        -------
        dict[str, str]
            Anthropic headers.
        """

        headers = super().build_headers()
        headers["anthropic-version"] = "2023-06-01"
        headers["x-api-key"] = self.api_key
        return headers

    def build_payload(self, *, input_data: str, model_ref: str) -> dict[str, t.Any]:
        """Build the Anthropic JSON payload.

        Parameters
        ----------
        input_data : str
            Plain text input to count.
        model_ref : str
            Anthropic model identifier.

        Returns
        -------
        dict[str, Any]
            Anthropic JSON payload.
        """

        return {
            "messages": [{"content": input_data, "role": "user"}],
            "model": model_ref,
        }

    def parse_token_count(self, *, data: dict[str, t.Any]) -> int:
        """Parse the Anthropic token count response.

        Parameters
        ----------
        data : dict[str, Any]
            Anthropic response body.

        Returns
        -------
        int
            Parsed token count.
        """

        input_tokens = data.get("input_tokens")
        if not isinstance(input_tokens, int):
            raise TokenCountError(
                provider_id=self.provider_id,
                message="expected integer field 'input_tokens'",
            )
        return input_tokens
