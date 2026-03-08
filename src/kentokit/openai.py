"""Public OpenAI request models."""

import typing as t
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class OpenAICountTokensRequest:
    """Validated OpenAI token count request payload.

    Parameters
    ----------
    model : str
        OpenAI model identifier.
    input : str
        Input text sent to the count-tokens endpoint.
    """

    model: str
    input: str

    def __post_init__(self) -> None:
        """Validate runtime field types.

        Raises
        ------
        TypeError
            If ``model`` or ``input`` is not a string.
        """

        if not isinstance(self.model, str):
            raise TypeError("model must be a string")
        if not isinstance(self.input, str):
            raise TypeError("input must be a string")

    def to_payload(self) -> dict[str, t.Any]:
        """Serialize the request into the OpenAI JSON payload.

        Returns
        -------
        dict[str, Any]
            JSON-compatible payload expected by the OpenAI provider transport.
        """

        return {
            "input": self.input,
            "model": self.model,
        }


__all__ = ["OpenAICountTokensRequest"]
