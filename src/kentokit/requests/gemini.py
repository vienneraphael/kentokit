"""Public Gemini request models."""

import typing as t
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GeminiCountTokensRequest:
    """Validated Gemini token count request payload.

    Parameters
    ----------
    model : str
        Gemini model identifier.
    contents : list[dict[str, Any]] | None, default=None
        Optional Gemini contents payload sent directly to ``countTokens``.
    generate_content_request : dict[str, Any] | None, default=None
        Optional full Gemini ``generateContentRequest`` payload.
    """

    model: str
    contents: list[dict[str, t.Any]] | None = None
    generate_content_request: dict[str, t.Any] | None = None

    def __post_init__(self) -> None:
        """Validate runtime field types.

        Raises
        ------
        TypeError
            If a field does not match the supported container type or if the
            request form is ambiguous.
        """

        if not isinstance(self.model, str):
            raise TypeError("model must be a string")
        if self.contents is not None and not isinstance(self.contents, list):
            raise TypeError("contents must be a list or None")
        if isinstance(self.contents, list) and not all(
            isinstance(content, dict) for content in self.contents
        ):
            raise TypeError("contents must contain dictionaries")
        if self.generate_content_request is not None and not isinstance(
            self.generate_content_request, dict
        ):
            raise TypeError("generate_content_request must be a dictionary or None")
        if self.contents is None and self.generate_content_request is None:
            raise TypeError("exactly one of contents or generate_content_request must be provided")
        if self.contents is not None and self.generate_content_request is not None:
            raise TypeError("exactly one of contents or generate_content_request must be provided")

    def to_payload(self) -> dict[str, t.Any]:
        """Serialize the request into the Gemini JSON payload.

        Returns
        -------
        dict[str, Any]
            JSON-compatible payload expected by the Gemini provider transport.
        """

        if self.contents is not None:
            return {"contents": self.contents}
        return {"generateContentRequest": self.generate_content_request}


__all__ = ["GeminiCountTokensRequest"]
