from typing import Any

from .deepseek_provider import DeepSeekProvider
from .groq_provider import GroqProvider
from .lmstudio_provider import LMStudioProvider
from .ollama_provider import OllamaProvider
from .openai_provider import OpenAIProvider

# ---------------------------------------------------------
# OPTIONAL PROVIDERS
# ---------------------------------------------------------

AnthropicProvider: Any
GeminiProvider: Any

try:
    from .anthropic_provider import AnthropicProvider
except ImportError:
    AnthropicProvider = None

try:
    from .gemini_provider import GeminiProvider
except ImportError:
    GeminiProvider = None


__all__ = [
    "OpenAIProvider",
    "LMStudioProvider",
    "DeepSeekProvider",
    "OllamaProvider",
    "GroqProvider",
    "AnthropicProvider",
    "GeminiProvider",
]
