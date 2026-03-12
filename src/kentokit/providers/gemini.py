"""Gemini token count provider."""

from __future__ import annotations

import typing as t
from urllib.parse import quote

import httpx

from kentokit.modalities import GeminiModality
from kentokit.providers.base import ProviderBase, TokenCountError
from kentokit.requests.gemini import GeminiCountTokensRequest

if t.TYPE_CHECKING:
    from kentokit.token_count import TokenCount


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

    @t.overload
    def count_token_count(
        self,
        *,
        input_data: str,
        model_ref: str,
        client: httpx.Client | None = None,
    ) -> TokenCount: ...

    @t.overload
    def count_token_count(
        self,
        *,
        request: GeminiCountTokensRequest,
        client: httpx.Client | None = None,
    ) -> TokenCount: ...

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
            return self.count_token_count(request=request, client=client).total

        if input_data is None:
            raise TypeError("input_data must be provided when request is not set")
        if model_ref is None:
            raise TypeError("model_ref must be provided when request is not set")
        return self.count_token_count(
            input_data=input_data,
            model_ref=model_ref,
            client=client,
        ).total

    def count_token_count(
        self,
        *,
        input_data: str | None = None,
        model_ref: str | None = None,
        client: httpx.Client | None = None,
        request: GeminiCountTokensRequest | None = None,
    ) -> TokenCount:
        """Count Gemini input tokens and return normalized metadata.

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
        TokenCount
            Normalized token count and optional Gemini metadata.

        Raises
        ------
        TypeError
            If the caller mixes incompatible arguments or omits required ones.
        """

        if request is not None:
            if input_data is not None or model_ref is not None:
                raise TypeError("request cannot be combined with input_data or model_ref")
            return self._count_request_token_count(request=request, client=client)

        if input_data is None:
            raise TypeError("input_data must be provided when request is not set")
        if model_ref is None:
            raise TypeError("model_ref must be provided when request is not set")
        return self._count_payload_token_count(
            model_ref=model_ref,
            payload=self.build_payload(input_data=input_data, model_ref=model_ref),
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

    def _count_request_token_count(
        self,
        *,
        request: GeminiCountTokensRequest,
        client: httpx.Client | None = None,
    ) -> TokenCount:
        """Count tokens for a pre-validated Gemini request payload.

        Parameters
        ----------
        request : GeminiCountTokensRequest
            Validated Gemini request payload.
        client : httpx.Client | None, default=None
            Optional client used for testing or client reuse.

        Returns
        -------
        TokenCount
            Normalized token count and optional Gemini metadata.
        """

        return self._count_payload_token_count(
            model_ref=request.model,
            payload=request.to_payload(),
            client=client,
        )

    def _count_payload_token_count(
        self,
        *,
        model_ref: str,
        payload: dict[str, t.Any],
        client: httpx.Client | None = None,
    ) -> TokenCount:
        """Count tokens for a Gemini payload and return normalized metadata.

        Parameters
        ----------
        model_ref : str
            Gemini model identifier.
        payload : dict[str, Any]
            JSON payload sent to the Gemini endpoint.
        client : httpx.Client | None, default=None
            Optional client used for testing or client reuse.

        Returns
        -------
        TokenCount
            Normalized token count and optional Gemini metadata.
        """

        url = self.build_url(model_ref=model_ref)
        headers = self.build_headers()

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

        return self.parse_token_count_response(data=response_data)

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

        return self.parse_token_count_response(data=data).total

    def parse_token_count_response(self, *, data: dict[str, t.Any]) -> TokenCount:
        """Parse the full Gemini token count response.

        Parameters
        ----------
        data : dict[str, Any]
            Gemini response body.

        Returns
        -------
        TokenCount
            Normalized token count and optional Gemini metadata.
        """

        from kentokit.token_count import TokenCount

        total_tokens = data.get("totalTokens")
        if not isinstance(total_tokens, int):
            raise TokenCountError(
                provider_id=self.provider_id,
                message="expected integer field 'totalTokens'",
            )

        cached_tokens = self._parse_optional_int_field(
            data=data,
            field_name="cachedContentTokenCount",
        )
        token_details = self._parse_optional_details_field(
            data=data,
            field_name="promptTokensDetails",
        )
        cache_token_details = self._parse_optional_details_field(
            data=data,
            field_name="cacheTokensDetails",
        )
        return TokenCount(
            total=total_tokens,
            cached_tokens=cached_tokens,
            token_details=token_details,
            cache_token_details=cache_token_details,
        )

    def _parse_optional_int_field(
        self,
        *,
        data: dict[str, t.Any],
        field_name: str,
    ) -> int | None:
        """Parse an optional integer field from the Gemini response.

        Parameters
        ----------
        data : dict[str, Any]
            Gemini response body.
        field_name : str
            Response field name to validate.

        Returns
        -------
        int | None
            Parsed integer value, when present.
        """

        value = data.get(field_name)
        if value is None:
            return None
        if not isinstance(value, int):
            raise TokenCountError(
                provider_id=self.provider_id,
                message=f"expected integer field '{field_name}'",
            )
        return value

    def _parse_optional_details_field(
        self,
        *,
        data: dict[str, t.Any],
        field_name: str,
    ) -> dict[GeminiModality, int] | None:
        """Parse an optional Gemini modality breakdown field.

        Parameters
        ----------
        data : dict[str, Any]
            Gemini response body.
        field_name : str
            Response field name to validate.

        Returns
        -------
        dict[GeminiModality, int] | None
            Validated Gemini modality breakdown, when present.
        """

        raw_value = data.get(field_name)
        if raw_value is None:
            return None
        if not isinstance(raw_value, list):
            raise TokenCountError(
                provider_id=self.provider_id,
                message=f"expected list field '{field_name}'",
            )

        parsed_details: dict[GeminiModality, int] = {}
        for index, raw_detail in enumerate(raw_value):
            if not isinstance(raw_detail, dict):
                raise TokenCountError(
                    provider_id=self.provider_id,
                    message=f"expected dictionary item '{field_name}[{index}]'",
                )
            modality = raw_detail.get("modality")
            token_count = raw_detail.get("tokenCount")
            if not isinstance(modality, str):
                raise TokenCountError(
                    provider_id=self.provider_id,
                    message=f"expected string field '{field_name}[{index}].modality'",
                )
            try:
                parsed_modality = GeminiModality(modality)
            except ValueError as exc:
                raise TokenCountError(
                    provider_id=self.provider_id,
                    message=f"expected valid Gemini modality in '{field_name}[{index}].modality'",
                ) from exc
            if not isinstance(token_count, int):
                raise TokenCountError(
                    provider_id=self.provider_id,
                    message=f"expected integer field '{field_name}[{index}].tokenCount'",
                )
            if parsed_modality in parsed_details:
                raise TokenCountError(
                    provider_id=self.provider_id,
                    message=(f"expected unique modality in '{field_name}[{index}].modality'"),
                )

            parsed_details[parsed_modality] = token_count

        return parsed_details

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
