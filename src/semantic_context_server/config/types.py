from typing import Literal, TypedDict

ProfileName = Literal["local", "hybrid", "cloud"]
StorageType = Literal["json", "chroma", "inmemory"]
EmbeddingProvider = Literal["openai", "sentence", "ollama", "lmstudio", "gemini"]
LLMProvider = Literal["openai", "lmstudio", "ollama", "groq", "anthropic"]
Environment = Literal["test", "dev", "prod"]


class EmbeddingDefaults(TypedDict):
    provider: str
    model: str
    dimension: int
