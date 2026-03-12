"""Public Bedrock request models."""

import json
import typing as t
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BedrockCountTokensRequest:
    """Validated Bedrock token count request payload.

    Parameters
    ----------
    model : str
        Bedrock model identifier.
    region : str
        AWS region for the Bedrock Runtime endpoint.
    converse : dict[str, Any] | None, default=None
        Optional Bedrock ``converse`` input payload.
    invoke_model_body : str | dict[str, Any] | None, default=None
        Optional JSON string or JSON-compatible dictionary used for the
        ``invokeModel`` token-count path.
    """

    model: str
    region: str
    converse: dict[str, t.Any] | None = None
    invoke_model_body: str | dict[str, t.Any] | None = None

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
        if not isinstance(self.region, str):
            raise TypeError("region must be a string")
        if self.converse is not None and not isinstance(self.converse, dict):
            raise TypeError("converse must be a dictionary or None")
        if self.invoke_model_body is not None and not isinstance(
            self.invoke_model_body,
            (str, dict),
        ):
            raise TypeError("invoke_model_body must be a string, a dictionary, or None")
        if self.converse is None and self.invoke_model_body is None:
            raise TypeError("exactly one of converse or invoke_model_body must be provided")
        if self.converse is not None and self.invoke_model_body is not None:
            raise TypeError("exactly one of converse or invoke_model_body must be provided")

    def to_payload(self) -> dict[str, t.Any]:
        """Serialize the request into the Bedrock JSON payload.

        Returns
        -------
        dict[str, Any]
            JSON-compatible payload expected by the Bedrock provider transport.
        """

        if self.converse is not None:
            return {"input": {"converse": self.converse}}

        body = self.invoke_model_body
        if isinstance(body, dict):
            body = json.dumps(body)
        return {"input": {"invokeModel": {"body": body}}}


__all__ = ["BedrockCountTokensRequest"]
