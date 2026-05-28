import re

from packages.features.llm_gateway.contracts import LLMGatewayContract
from packages.features.llm_gateway.dto import LLMRequest, LLMResponse


class FakeLLMService(LLMGatewayContract):
    def __init__(
        self,
        result: str | None = None,
        fail: bool = False,
        debug: bool = False,
        context_service=None,
        graph=None,
    ) -> None:
        self.result = result
        self.fail = fail
        self.debug = debug

        self.context_service = context_service
        self.graph = graph

        self.calls: list[LLMRequest] = []
        self.calls_by_campaign: dict[str, list[LLMRequest]] = {}

    # ==========================================================
    # MAIN
    # ==========================================================

    async def generate(self, request: LLMRequest) -> LLMResponse:
        if not isinstance(request, LLMRequest):
            raise TypeError("FakeLLMService espera LLMRequest")

        if not request.prompt:
            raise TypeError("LLMRequest must contain a prompt")

        self.calls.append(request)

        if request.campaign_id:
            self.calls_by_campaign.setdefault(request.campaign_id, []).append(request)

        request = await self._enrich_request(request)

        if self.debug:
            self._debug_prompt(request.prompt)

        if self.fail:
            raise RuntimeError("Fake LLM failure")

        if self.result is not None:
            return self._response(self.result)

        prompt = request.prompt.lower()

        action = self._extract_action(prompt)
        memory = self._extract_memory(prompt)

        content = self._resolve_response(action, memory)

        return self._response(content)

    # ==========================================================
    # RAG ENRICHMENT (ALINHADO COM LLMService)
    # ==========================================================

    async def _enrich_request(self, request: LLMRequest) -> LLMRequest:
        prompt = request.prompt

        if self.context_service:
            try:
                context = await self.context_service.search(prompt)
                if context:
                    prompt = "[Contexto]\n" + "\n".join(context[:5]) + f"\n\n{prompt}"
            except Exception:
                pass

        if self.graph:
            try:
                hint = await self.graph.build_hint(prompt)
                if hint:
                    prompt = f"{hint}\n\n{prompt}"
            except Exception:
                pass

        return request.copy_with(prompt=prompt)

    # ==========================================================
    # 🧠 MEMORY EXTRACTION
    # ==========================================================

    def _extract_memory(self, prompt: str) -> list[str]:
        lines = prompt.splitlines()
        memory = []

        capture = False

        for line in lines:
            line = line.strip()

            if any(
                key in line.lower()
                for key in [
                    "eventos recentes",
                    "histórico",
                    "resumo da campanha",
                    "contexto relevante",
                    "contexto",
                ]
            ):
                capture = True
                continue

            if capture:
                if not line:
                    capture = False
                    continue

                cleaned = line.lstrip("- ").strip()
                if cleaned:
                    memory.append(cleaned)

        return memory

    # ==========================================================
    # 🎯 CORE (DETERMINÍSTICO)
    # ==========================================================

    def _resolve_response(self, action: str, memory: list[str]) -> str:
        action = action.lower()
        has_sword = any("sword" in m for m in memory)
        has_key = any("key" in m for m in memory)

        return (
            self._resolve_attack(action, has_sword)
            or self._resolve_pick(action)
            or self._resolve_open(action, has_key)
            or self._resolve_look(action, memory)
            or f"you {action}"
        )

    def _resolve_attack(self, action: str, has_sword: bool) -> str:
        if "attack" not in action:
            return ""
        match = re.search(r"attack\s+(?:the\s+)?(\w+)", action)
        target = f" the {match.group(1)}" if match else ""
        weapon = " with your sword" if has_sword else ""
        return f"you attack{target}{weapon}"

    def _resolve_pick(self, action: str) -> str:
        if not any(k in action for k in ["pick", "grab", "take"]):
            return ""
        if "key" in action:
            return "you pick up a key"
        if "sword" in action:
            return "you pick up a sword"
        return ""

    def _resolve_open(self, action: str, has_key: bool) -> str:
        if "open" not in action:
            return ""
        if "chest" in action:
            return "you open the chest with the key" if has_key else "you open the chest"
        if "door" in action:
            return "you open the door"
        return ""

    def _resolve_look(self, action: str, memory: list[str]) -> str:
        if "look" not in action:
            return ""
        return f"you notice {memory[-1]}" if memory else "you look around"

    # ==========================================================
    # EXTRACTION
    # ==========================================================

    def _extract_action(self, prompt: str) -> str:
        # current format: [Ação do jogador]\n<action>
        match = re.search(r"ação do jogador[:\]]\s*[\n\r]+([^\n\r]+)", prompt)
        if match:
            return match.group(1).strip()
        # legacy format: Ação do jogador: <action> (same line)
        match = re.search(r"ação do jogador:\s*(.+)", prompt)
        if match:
            return match.group(1).strip()
        return prompt

    # ==========================================================
    # STREAM (mínimo viável)
    # ==========================================================

    async def stream(self, request: LLMRequest):
        response = await self.generate(request)
        yield response.content

    # ==========================================================
    # HELPERS
    # ==========================================================

    def _response(self, content: str) -> LLMResponse:
        return LLMResponse(
            content=content,
            provider="fake",
            model="fake-model",
        )

    def _debug_prompt(self, prompt: str) -> None:
        print("\n=== PROMPT DEBUG ===")
        print(prompt)
        print("====================\n")
