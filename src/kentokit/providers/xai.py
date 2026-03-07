"""xAI token count provider."""

import typing as t

from kentokit.providers.base import ProviderBase, TokenCountError


class XAIProvider(ProviderBase):
    """xAI token counting implementation."""

    provider_id = "xai"

    def build_url(self, *, model_ref: str) -> str:
        """Build the xAI token count URL.

        Parameters
        ----------
        model_ref : str
            xAI model identifier.

        Returns
        -------
        str
            xAI token count endpoint.
        """

        return "https://api.x.ai/v1/tokenize-text"

    def build_headers(self) -> dict[str, str]:
        """Build xAI request headers.

        Returns
        -------
        dict[str, str]
            xAI headers.
        """

        headers = super().build_headers()
        headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def build_payload(self, *, input_data: str, model_ref: str) -> dict[str, t.Any]:
        """Build the xAI JSON payload.

        Parameters
        ----------
        input_data : str
            Plain text input to count.
        model_ref : str
            xAI model identifier.

        Returns
        -------
        dict[str, Any]
            xAI JSON payload.
        """

        return {"model": model_ref, "text": input_data}

    def parse_token_count(self, *, data: dict[str, t.Any]) -> int:
        """Parse the xAI token count response.

        Parameters
        ----------
        data : dict[str, Any]
            xAI response body.

        Returns
        -------
        int
            Parsed token count.
        """

        token_ids = data.get("token_ids")
        if token_ids is None:
            token_ids = data.get("tokenIds")

        if not isinstance(token_ids, list) or not all(
            isinstance(token_id, int) for token_id in token_ids
        ):
            raise TokenCountError(
                provider_id=self.provider_id,
                message="expected integer list field 'token_ids'",
            )
        return len(token_ids)
