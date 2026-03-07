"""OpenAI token count provider."""

import typing as t

from kentokit.providers.base import ProviderBase, ProviderResponseError


class OpenAIProvider(ProviderBase):
    """OpenAI token counting implementation."""

    provider_id = "openai"

    def build_url(self, *, model_ref: str) -> str:
        """Build the OpenAI token count URL.

        Parameters
        ----------
        model_ref : str
            OpenAI model identifier.

        Returns
        -------
        str
            OpenAI token count endpoint.
        """

        return "https://api.openai.com/v1/responses/input_tokens"

    def build_headers(self) -> dict[str, str]:
        """Build OpenAI request headers.

        Returns
        -------
        dict[str, str]
            OpenAI headers.
        """

        headers = super().build_headers()
        headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def build_payload(self, *, input_data: str, model_ref: str) -> dict[str, t.Any]:
        """Build the OpenAI JSON payload.

        Parameters
        ----------
        input_data : str
            Plain text input to count.
        model_ref : str
            OpenAI model identifier.

        Returns
        -------
        dict[str, Any]
            OpenAI JSON payload.
        """

        return {"input": input_data, "model": model_ref}

    def parse_token_count(self, *, data: dict[str, t.Any]) -> int:
        """Parse the OpenAI token count response.

        Parameters
        ----------
        data : dict[str, Any]
            OpenAI response body.

        Returns
        -------
        int
            Parsed token count.
        """

        input_tokens = data.get("input_tokens")
        if not isinstance(input_tokens, int):
            raise ProviderResponseError(
                provider_id=self.provider_id,
                message="expected integer field 'input_tokens'",
            )
        return input_tokens
