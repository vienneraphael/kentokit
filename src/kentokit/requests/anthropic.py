"""Public Anthropic request models."""

import typing as t
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AnthropicCountTokensRequest:
    """Validated Anthropic token count request payload.

    Parameters
    ----------
    model : str
        Anthropic model identifier.
    messages : list[dict[str, Any]]
        Anthropic Messages API payload blocks.
    system : str | list[dict[str, Any]] | None, default=None
        Optional Anthropic system prompt content.
    tools : list[dict[str, Any]] | None, default=None
        Optional Anthropic tool definitions.
    tool_choice : dict[str, Any] | None, default=None
        Optional Anthropic tool choice configuration.
    """

    model: str
    messages: list[dict[str, t.Any]]
    system: str | list[dict[str, t.Any]] | None = None
    tools: list[dict[str, t.Any]] | None = None
    tool_choice: dict[str, t.Any] | None = None

    def __post_init__(self) -> None:
        """Validate runtime field types.

        Raises
        ------
        TypeError
            If a field does not match the supported container type.
        """

        if not isinstance(self.model, str):
            raise TypeError("model must be a string")
        if not isinstance(self.messages, list):
            raise TypeError("messages must be a list")
        if not all(isinstance(message, dict) for message in self.messages):
            raise TypeError("messages must contain dictionaries")
        if self.system is not None and not isinstance(self.system, (str, list)):
            raise TypeError("system must be a string, a list, or None")
        if isinstance(self.system, list) and not all(
            isinstance(block, dict) for block in self.system
        ):
            raise TypeError("system lists must contain dictionaries")
        if self.tools is not None and not isinstance(self.tools, list):
            raise TypeError("tools must be a list or None")
        if isinstance(self.tools, list) and not all(isinstance(tool, dict) for tool in self.tools):
            raise TypeError("tools must contain dictionaries")
        if self.tool_choice is not None and not isinstance(self.tool_choice, dict):
            raise TypeError("tool_choice must be a dictionary or None")

    def to_payload(self) -> dict[str, t.Any]:
        """Serialize the request into the Anthropic JSON payload.

        Returns
        -------
        dict[str, Any]
            JSON-compatible payload expected by the Anthropic provider transport.
        """

        payload: dict[str, t.Any] = {
            "messages": self.messages,
            "model": self.model,
        }
        if self.system is not None:
            payload["system"] = self.system
        if self.tools is not None:
            payload["tools"] = self.tools
        if self.tool_choice is not None:
            payload["tool_choice"] = self.tool_choice
        return payload


__all__ = ["AnthropicCountTokensRequest"]
