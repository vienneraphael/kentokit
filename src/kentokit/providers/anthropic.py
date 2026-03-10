"""Anthropic token count provider."""

import typing as t

import httpx

from kentokit.providers.base import ProviderBase, TokenCountError
from kentokit.requests.anthropic import AnthropicCountTokensRequest


class AnthropicProvider(ProviderBase):
    """Anthropic token counting implementation."""

    provider_id = "anthropic"

    @t.overload
    def count_tokens(
        self,
        *,
        input_data: str,
        model_ref: str,
        client: httpx.Client | None = None,
    ) -> int: ...

    @t.overload
    def count_tokens(
        self,
        *,
        request: AnthropicCountTokensRequest,
        client: httpx.Client | None = None,
    ) -> int: ...

    def count_tokens(
        self,
        *,
        input_data: str | None = None,
        model_ref: str | None = None,
        client: httpx.Client | None = None,
        request: AnthropicCountTokensRequest | None = None,
    ) -> int:
        """Count Anthropic input tokens.

        Parameters
        ----------
        input_data : str | None, default=None
            Plain text input to count.
        model_ref : str | None, default=None
            Anthropic model identifier used with ``input_data``.
        client : httpx.Client | None, default=None
            Optional client used for testing or client reuse.
        request : AnthropicCountTokensRequest | None, default=None
            Validated Anthropic request payload. When provided, ``input_data``
            and ``model_ref`` must be omitted.

        Returns
        -------
        int
            Number of input tokens reported by the provider.

        Raises
        ------
        TypeError
            If the caller mixes incompatible arguments or omits required ones.
        """

        if request is not None:
            if input_data is not None or model_ref is not None:
                raise TypeError("request cannot be combined with input_data or model_ref")
            return self._count_request_tokens(request=request, client=client)

        if input_data is None:
            raise TypeError("input_data must be provided when request is not set")
        if model_ref is None:
            raise TypeError("model_ref must be provided when request is not set")
        return super().count_tokens(
            input_data=input_data,
            model_ref=model_ref,
            client=client,
        )

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

    def _count_request_tokens(
        self,
        *,
        request: AnthropicCountTokensRequest,
        client: httpx.Client | None = None,
    ) -> int:
        """Count tokens for a pre-validated Anthropic request payload.

        Parameters
        ----------
        request : AnthropicCountTokensRequest
            Validated Anthropic request payload.
        client : httpx.Client | None, default=None
            Optional client used for testing or client reuse.

        Returns
        -------
        int
            Number of input tokens reported by the provider.
        """

        url = self.build_url(model_ref=request.model)
        headers = self.build_headers()
        payload = request.to_payload()

        if client is None:
            with httpx.Client(timeout=self.timeout_seconds) as managed_client:
                response_data = self._post_json(
                    client=managed_client,
                    url=url,
                    headers=headers,
                    payload=payload,
                )
        else:
            response_data = self._post_json(
                client=client,
                url=url,
                headers=headers,
                payload=payload,
            )

        return self.parse_token_count(data=response_data)

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
