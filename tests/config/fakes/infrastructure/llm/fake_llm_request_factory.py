from packages.features.llm_gateway.dto import LLMRequest


class FakeLLMRequestFactory:
    @staticmethod
    def create(
        prompt: str = "ação do jogador: look",
        campaign_id: str = "test-campaign",
        **overrides,
    ) -> LLMRequest:
        return LLMRequest(
            prompt=prompt,
            campaign_id=campaign_id,
            system_prompt=overrides.get("system_prompt"),
            temperature=overrides.get("temperature", 0.7),
            max_tokens=overrides.get("max_tokens", 1000),
            timeout=overrides.get("timeout"),
            metadata=overrides.get("metadata", {}),
            intent=overrides.get("intent"),
        )

    @staticmethod
    def simple(prompt: str = "look") -> LLMRequest:
        return LLMRequest(
            prompt=f"ação do jogador: {prompt}",
            campaign_id="test",
        )
