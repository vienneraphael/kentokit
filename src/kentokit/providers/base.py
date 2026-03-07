"""Base abstractions for provider token counting."""

from __future__ import annotations

import abc
import typing as t

import httpx

ProviderId = t.Literal["openai", "anthropic", "gemini", "xai"]


class TokenCountError(Exception):
    """Base exception for token counting failures."""


class UnsupportedProviderError(TokenCountError):
    """Raised when a provider id is not supported."""

    def __init__(self, *, provider_id: str) -> None:
        self.provider_id = provider_id
        super().__init__(f"Unsupported token counting provider: {provider_id}")


class ProviderHTTPError(TokenCountError):
    """Raised when the HTTP request to a provider fails."""

    def __init__(
        self,
        *,
        provider_id: str,
        message: str,
        status_code: int | None = None,
        response_text: str | None = None,
    ) -> None:
        self.provider_id = provider_id
        self.message = message
        self.status_code = status_code
        self.response_text = response_text

        status_fragment = "" if status_code is None else f" (status {status_code})"
        response_fragment = ""
        if response_text:
            response_fragment = f": {response_text}"
        super().__init__(
            f"{provider_id} token counting request failed{status_fragment}: "
            f"{message}{response_fragment}"
        )


class ProviderResponseError(TokenCountError):
    """Raised when a provider response cannot be parsed."""

    def __init__(self, *, provider_id: str, message: str) -> None:
        self.provider_id = provider_id
        self.message = message
        super().__init__(f"{provider_id} returned an invalid token count response: {message}")


class ProviderBase(abc.ABC):
    """Base class for HTTP token count providers."""

    provider_id: ProviderId
    timeout_seconds: float = 10.0

    def __init__(self, *, api_key: str) -> None:
        self.api_key = api_key

    def count_tokens(
        self,
        *,
        input_data: str,
        model_ref: str,
        client: httpx.Client | None = None,
    ) -> int:
        """Count input tokens for plain text input.

        Parameters
        ----------
        input_data : str
            Plain text input to count.
        model_ref : str
            Provider-specific model identifier.
        client : httpx.Client | None, default=None
            Optional client used for testing or client reuse.

        Returns
        -------
        int
            Number of input tokens reported by the provider.
        """

        url = self.build_url(model_ref=model_ref)
        headers = self.build_headers()
        payload = self.build_payload(input_data=input_data, model_ref=model_ref)

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

    def build_headers(self) -> dict[str, str]:
        """Build headers for the provider request.

        Returns
        -------
        dict[str, str]
            Headers to send with the HTTP request.
        """

        return {"Content-Type": "application/json"}

    @abc.abstractmethod
    def build_url(self, *, model_ref: str) -> str:
        """Build the full provider URL.

        Parameters
        ----------
        model_ref : str
            Provider-specific model identifier.

        Returns
        -------
        str
            Absolute URL for the provider request.
        """

    @abc.abstractmethod
    def build_payload(self, *, input_data: str, model_ref: str) -> dict[str, t.Any]:
        """Build the provider-specific JSON payload.

        Parameters
        ----------
        input_data : str
            Plain text input to count.
        model_ref : str
            Provider-specific model identifier.

        Returns
        -------
        dict[str, Any]
            JSON payload sent to the provider.
        """

    @abc.abstractmethod
    def parse_token_count(self, *, data: dict[str, t.Any]) -> int:
        """Extract the token count from the provider response.

        Parameters
        ----------
        data : dict[str, Any]
            Decoded provider JSON response.

        Returns
        -------
        int
            Parsed token count.
        """

    def _post_json(
        self,
        *,
        client: httpx.Client,
        url: str,
        headers: dict[str, str],
        payload: dict[str, t.Any],
    ) -> dict[str, t.Any]:
        """Send a JSON POST request and decode the response.

        Parameters
        ----------
        client : httpx.Client
            HTTP client used to execute the request.
        url : str
            Absolute provider URL.
        headers : dict[str, str]
            Request headers.
        payload : dict[str, Any]
            JSON request body.

        Returns
        -------
        dict[str, Any]
            Decoded JSON response.

        Raises
        ------
        ProviderHTTPError
            If the request fails or returns a non-success status.
        ProviderResponseError
            If the response body is not valid JSON.
        """

        try:
            response = client.post(url=url, headers=headers, json=payload)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise ProviderHTTPError(
                provider_id=self.provider_id,
                message="provider returned a non-success status",
                status_code=exc.response.status_code,
                response_text=exc.response.text,
            ) from exc
        except httpx.HTTPError as exc:
            raise ProviderHTTPError(
                provider_id=self.provider_id,
                message=str(exc),
            ) from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise ProviderResponseError(
                provider_id=self.provider_id,
                message="response body is not valid JSON",
            ) from exc

        if not isinstance(data, dict):
            raise ProviderResponseError(
                provider_id=self.provider_id,
                message="response body must be a JSON object",
            )
        return data
