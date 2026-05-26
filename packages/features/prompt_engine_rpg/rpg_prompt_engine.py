from __future__ import annotations

from typing import Any

from packages.features.prompt_engine_core import NarrativeBuilder
from packages.features.prompt_engine_core.contracts import NarrativePromptBuilderContract


class RPGPromptEngine:
    """RPG-specialized prompt engine built on top of core prompt contracts."""

    def __init__(self, core: NarrativePromptBuilderContract | None = None) -> None:
        self.core = core or NarrativeBuilder()

    def build_system_prompt(self, scene_type: str | None = None) -> str:
        base = self.core.build_system_prompt(scene_type=scene_type)
        return base + " Mantenha continuidade entre cenas e consequências persistentes."

    def build_user_prompt(self, ctx: dict[str, Any], action: str) -> str:
        prompt = self.core.build_user_prompt(ctx=ctx, action=action)
        return prompt + "\n\n[Diretriz RPG]\nConsidere rolagens, risco e estado da campanha."

    def build_narrative_request(
        self, ctx: dict[str, Any], action: str, scene_type: str | None = None
    ) -> dict[str, Any]:
        return {
            "system_prompt": self.build_system_prompt(scene_type=scene_type),
            "prompt": self.build_user_prompt(ctx=ctx, action=action),
        }

    def get_generation_config(self, scene_type: str | None) -> dict[str, Any]:
        return self.core.get_generation_config(scene_type)

    def sanitize_output(self, text: str) -> str:
        return self.core.sanitize_output(text)

    def normalize_action(self, action: str) -> str:
        return self.core.normalize_action(action)

    def enforce_length(self, text: str, max_chars: int) -> str:
        return self.core.enforce_length(text, max_chars)
