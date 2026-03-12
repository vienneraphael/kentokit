"""Provider registry for token counting."""

from kentokit.providers.anthropic import AnthropicProvider
from kentokit.providers.base import ProviderBase, ProviderId
from kentokit.providers.bedrock import BedrockProvider
from kentokit.providers.gemini import GeminiProvider
from kentokit.providers.openai import OpenAIProvider
from kentokit.providers.xai import XAIProvider

PROVIDER_REGISTRY: dict[ProviderId, type[ProviderBase]] = {
    "anthropic": AnthropicProvider,
    "bedrock": BedrockProvider,
    "gemini": GeminiProvider,
    "openai": OpenAIProvider,
    "xai": XAIProvider,
}

__all__ = ["PROVIDER_REGISTRY"]
