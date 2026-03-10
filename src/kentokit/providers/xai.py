"""xAI token count provider."""

from __future__ import annotations

import typing as t

import httpx

from kentokit.providers.base import ProviderBase, TokenCountError
from kentokit.requests.xai import XAICountTokensRequest


class XAIProvider(ProviderBase):
    """xAI token counting implementation."""

    provider_id = "xai"

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
        request: XAICountTokensRequest,
        client: httpx.Client | None = None,
    ) -> int: ...

    def count_tokens(
        self,
        *,
        input_data: str | None = None,
        model_ref: str | None = None,
        client: httpx.Client | None = None,
        request: XAICountTokensRequest | None = None,
    ) -> int:
        """Count xAI input tokens.

        Parameters
        ----------
        input_data : str | None, default=None
            Plain text input to count.
        model_ref : str | None, default=None
            xAI model identifier used with ``input_data``.
        client : httpx.Client | None, default=None
            Optional client used for testing or client reuse.
        request : XAICountTokensRequest | None, default=None
            Validated xAI request payload. When provided, ``input_data`` and
            ``model_ref`` must be omitted.

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

    def _count_request_tokens(
        self,
        *,
        request: XAICountTokensRequest,
        client: httpx.Client | None = None,
    ) -> int:
        """Count tokens for a pre-validated xAI request payload.

        Parameters
        ----------
        request : XAICountTokensRequest
            Validated xAI request payload.
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
        if token_ids is None:
            token_ids = data.get("tokens")

        if not isinstance(token_ids, list):
            raise TokenCountError(
                provider_id=self.provider_id,
                message="expected list field 'token_ids', 'tokenIds', or 'tokens'",
            )
        return len(token_ids)
