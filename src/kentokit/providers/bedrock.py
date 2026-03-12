"""Amazon Bedrock token count provider."""

from __future__ import annotations

import typing as t
from urllib.parse import quote

import httpx

from kentokit.providers.base import ProviderBase, TokenCountError
from kentokit.requests.bedrock import BedrockCountTokensRequest


class BedrockProvider(ProviderBase):
    """Amazon Bedrock token counting implementation."""

    provider_id = "bedrock"

    @t.overload
    def count_tokens(
        self,
        *,
        request: BedrockCountTokensRequest,
        client: httpx.Client | None = None,
    ) -> int: ...

    @t.overload
    def count_tokens(
        self,
        *,
        input_data: str,
        model_ref: str,
        client: httpx.Client | None = None,
    ) -> int: ...

    def count_tokens(
        self,
        *,
        input_data: str | None = None,
        model_ref: str | None = None,
        client: httpx.Client | None = None,
        request: BedrockCountTokensRequest | None = None,
    ) -> int:
        """Count Bedrock input tokens.

        Parameters
        ----------
        input_data : str | None, default=None
            Unsupported plain text input for Bedrock.
        model_ref : str | None, default=None
            Unsupported plain text model identifier for Bedrock.
        client : httpx.Client | None, default=None
            Optional client used for testing or client reuse.
        request : BedrockCountTokensRequest | None, default=None
            Validated Bedrock request payload. When provided, ``input_data`` and
            ``model_ref`` must be omitted.

        Returns
        -------
        int
            Number of input tokens reported by the provider.

        Raises
        ------
        TypeError
            If the caller omits ``request`` or mixes incompatible arguments.
        """

        if request is None:
            raise TypeError(
                "BedrockProvider requires request=BedrockCountTokensRequest; plain text input "
                "is not supported"
            )
        if input_data is not None or model_ref is not None:
            raise TypeError("request cannot be combined with input_data or model_ref")
        return self._count_request_tokens(request=request, client=client)

    def build_url(self, *, model_ref: str) -> str:
        """Reject plain text URL construction for Bedrock.

        Parameters
        ----------
        model_ref : str
            Unsupported plain text model identifier.

        Returns
        -------
        str
            This method does not return because Bedrock requires typed requests.
        """

        del model_ref
        raise TypeError(
            "BedrockProvider requires request=BedrockCountTokensRequest; plain text input is "
            "not supported"
        )

    def build_headers(self) -> dict[str, str]:
        """Build Bedrock request headers.

        Returns
        -------
        dict[str, str]
            Bedrock headers.
        """

        headers = super().build_headers()
        headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def build_payload(self, *, input_data: str, model_ref: str) -> dict[str, t.Any]:
        """Reject plain text payload construction for Bedrock.

        Parameters
        ----------
        input_data : str
            Unsupported plain text input.
        model_ref : str
            Unsupported plain text model identifier.

        Returns
        -------
        dict[str, Any]
            This method does not return because Bedrock requires typed requests.
        """

        del input_data, model_ref
        raise TypeError(
            "BedrockProvider requires request=BedrockCountTokensRequest; plain text input is "
            "not supported"
        )

    def _build_request_url(self, *, model: str, region: str) -> str:
        """Build the Bedrock token count URL for a typed request.

        Parameters
        ----------
        model : str
            Bedrock model identifier.
        region : str
            AWS region for the Bedrock Runtime endpoint.

        Returns
        -------
        str
            Bedrock token count endpoint.
        """

        return (
            f"https://bedrock-runtime.{region}.amazonaws.com/model/"
            f"{quote(model, safe='')}/count-tokens"
        )

    def _count_request_tokens(
        self,
        *,
        request: BedrockCountTokensRequest,
        client: httpx.Client | None = None,
    ) -> int:
        """Count tokens for a pre-validated Bedrock request payload.

        Parameters
        ----------
        request : BedrockCountTokensRequest
            Validated Bedrock request payload.
        client : httpx.Client | None, default=None
            Optional client used for testing or client reuse.

        Returns
        -------
        int
            Number of input tokens reported by the provider.
        """

        url = self._build_request_url(model=request.model, region=request.region)
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

    def parse_token_count(self, *, data: dict[str, t.Any]) -> int:
        """Parse the Bedrock token count response.

        Parameters
        ----------
        data : dict[str, Any]
            Bedrock response body.

        Returns
        -------
        int
            Parsed token count.
        """

        input_tokens = data.get("inputTokens")
        if not isinstance(input_tokens, int):
            raise TokenCountError(
                provider_id=self.provider_id,
                message="expected integer field 'inputTokens'",
            )
        return input_tokens
