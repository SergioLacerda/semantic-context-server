from __future__ import annotations

from typing import Protocol

from packages.features.prompt_engine_core.contracts import NarrativePromptBuilderContract


class RPGPromptBuilderContract(Protocol):
    def build_system_prompt(self, scene_type: str | None = None) -> str: ...
    def build_user_prompt(self, ctx: dict[str, str | list[str]], action: str) -> str: ...
    def get_generation_config(self, scene_type: str | None) -> dict[str, float | int]: ...
    def sanitize_output(self, text: str) -> str: ...


class RPGPromptEngineContract(Protocol):
    core: NarrativePromptBuilderContract

    def build_narrative_request(self, ctx: dict, action: str, scene_type: str | None = None) -> dict: ...
