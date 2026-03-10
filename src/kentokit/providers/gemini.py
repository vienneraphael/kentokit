"""Gemini token count provider."""

from __future__ import annotations

import typing as t
from urllib.parse import quote

import httpx

from kentokit.providers.base import ProviderBase, TokenCountError
from kentokit.requests.gemini import GeminiCountTokensRequest


class GeminiProvider(ProviderBase):
    """Gemini token counting implementation."""

    provider_id = "gemini"

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
        request: GeminiCountTokensRequest,
        client: httpx.Client | None = None,
    ) -> int: ...

    def count_tokens(
        self,
        *,
        input_data: str | None = None,
        model_ref: str | None = None,
        client: httpx.Client | None = None,
        request: GeminiCountTokensRequest | None = None,
    ) -> int:
        """Count Gemini input tokens.

        Parameters
        ----------
        input_data : str | None, default=None
            Plain text input to count.
        model_ref : str | None, default=None
            Gemini model identifier used with ``input_data``.
        client : httpx.Client | None, default=None
            Optional client used for testing or client reuse.
        request : GeminiCountTokensRequest | None, default=None
            Validated Gemini request payload. When provided, ``input_data`` and
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

    def _count_request_tokens(
        self,
        *,
        request: GeminiCountTokensRequest,
        client: httpx.Client | None = None,
    ) -> int:
        """Count tokens for a pre-validated Gemini request payload.

        Parameters
        ----------
        request : GeminiCountTokensRequest
            Validated Gemini request payload.
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
