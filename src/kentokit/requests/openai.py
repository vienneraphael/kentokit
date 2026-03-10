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
    input : str | list[dict[str, Any]] | None, default=None
        Optional Responses-style input sent to the count-tokens endpoint.
    conversation : str | dict[str, Any] | None, default=None
        Optional OpenAI conversation state for the count request.
    instructions : str | None, default=None
        Optional system or developer instructions applied to the request.
    parallel_tool_calls : bool | None, default=None
        Optional OpenAI parallel tool-calling setting.
    previous_response_id : str | None, default=None
        Optional prior response id used to continue an OpenAI conversation.
    reasoning : dict[str, Any] | None, default=None
        Optional OpenAI reasoning configuration.
    text : dict[str, Any] | None, default=None
        Optional OpenAI text output configuration.
    tool_choice : str | dict[str, Any] | None, default=None
        Optional OpenAI tool choice configuration.
    tools : list[dict[str, Any]] | None, default=None
        Optional OpenAI tool definitions.
    truncation : Literal["auto", "disabled"] | None, default=None
        Optional OpenAI truncation mode for the count request.
    """

    model: str
    input: str | list[dict[str, t.Any]] | None = None
    conversation: str | dict[str, t.Any] | None = None
    instructions: str | None = None
    parallel_tool_calls: bool | None = None
    previous_response_id: str | None = None
    reasoning: dict[str, t.Any] | None = None
    text: dict[str, t.Any] | None = None
    tool_choice: str | dict[str, t.Any] | None = None
    tools: list[dict[str, t.Any]] | None = None
    truncation: t.Literal["auto", "disabled"] | None = None

    def __post_init__(self) -> None:
        """Validate runtime field types.

        Raises
        ------
        TypeError
            If a field does not match the supported container type.
        """

        if not isinstance(self.model, str):
            raise TypeError("model must be a string")
        if self.input is not None and not isinstance(self.input, (str, list)):
            raise TypeError("input must be a string, a list, or None")
        if isinstance(self.input, list) and not all(isinstance(item, dict) for item in self.input):
            raise TypeError("input lists must contain dictionaries")
        if self.conversation is not None and not isinstance(self.conversation, (str, dict)):
            raise TypeError("conversation must be a string, a dictionary, or None")
        if self.instructions is not None and not isinstance(self.instructions, str):
            raise TypeError("instructions must be a string or None")
        if self.parallel_tool_calls is not None and not isinstance(self.parallel_tool_calls, bool):
            raise TypeError("parallel_tool_calls must be a boolean or None")
        if self.previous_response_id is not None and not isinstance(self.previous_response_id, str):
            raise TypeError("previous_response_id must be a string or None")
        if self.reasoning is not None and not isinstance(self.reasoning, dict):
            raise TypeError("reasoning must be a dictionary or None")
        if self.text is not None and not isinstance(self.text, dict):
            raise TypeError("text must be a dictionary or None")
        if self.tool_choice is not None and not isinstance(self.tool_choice, (str, dict)):
            raise TypeError("tool_choice must be a string, a dictionary, or None")
        if self.tools is not None and not isinstance(self.tools, list):
            raise TypeError("tools must be a list or None")
        if isinstance(self.tools, list) and not all(isinstance(tool, dict) for tool in self.tools):
            raise TypeError("tools must contain dictionaries")
        if self.truncation is not None and self.truncation not in ("auto", "disabled"):
            raise TypeError("truncation must be 'auto', 'disabled', or None")

    def to_payload(self) -> dict[str, t.Any]:
        """Serialize the request into the OpenAI JSON payload.

        Returns
        -------
        dict[str, Any]
            JSON-compatible payload expected by the OpenAI provider transport.
        """

        payload: dict[str, t.Any] = {"model": self.model}
        if self.input is not None:
            payload["input"] = self.input
        if self.conversation is not None:
            payload["conversation"] = self.conversation
        if self.instructions is not None:
            payload["instructions"] = self.instructions
        if self.parallel_tool_calls is not None:
            payload["parallel_tool_calls"] = self.parallel_tool_calls
        if self.previous_response_id is not None:
            payload["previous_response_id"] = self.previous_response_id
        if self.reasoning is not None:
            payload["reasoning"] = self.reasoning
        if self.text is not None:
            payload["text"] = self.text
        if self.tool_choice is not None:
            payload["tool_choice"] = self.tool_choice
        if self.tools is not None:
            payload["tools"] = self.tools
        if self.truncation is not None:
            payload["truncation"] = self.truncation
        return payload


__all__ = ["OpenAICountTokensRequest"]
