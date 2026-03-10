"""Public xAI request models."""

import typing as t
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class XAICountTokensRequest:
    """Validated xAI token count request payload.

    Parameters
    ----------
    model : str
        xAI model identifier.
    text : str
        Input text sent to the xAI tokenization endpoint.
    """

    model: str
    text: str

    def __post_init__(self) -> None:
        """Validate runtime field types.

        Raises
        ------
        TypeError
            If ``model`` or ``text`` is not a string.
        """

        if not isinstance(self.model, str):
            raise TypeError("model must be a string")
        if not isinstance(self.text, str):
            raise TypeError("text must be a string")

    def to_payload(self) -> dict[str, t.Any]:
        """Serialize the request into the xAI JSON payload.

        Returns
        -------
        dict[str, Any]
            JSON-compatible payload expected by the xAI provider transport.
        """

        return {
            "model": self.model,
            "text": self.text,
        }


__all__ = ["XAICountTokensRequest"]
