from __future__ import annotations

from typing import Any


class NarrativeBuilder:
    """Core prompt builder for narrative generation."""

    def build_system_prompt(self, scene_type: str | None = None) -> str:
        base = (
            "Você é um mestre de RPG narrativo. "
            "Descreva ações e consequências de forma imersiva, clara e coerente. "
            "Nunca fale fora do personagem (OOC)."
        )

        scene_instructions = {
            "COMBAT": " Foque em ação, impacto e dinamismo.",
            "EXPLORATION": " Foque em ambiente, descoberta e detalhes.",
            "SOCIAL": " Foque em diálogos e intenções.",
        }

        return base + scene_instructions.get(scene_type or "", "")

    def build_user_prompt(self, ctx: dict[str, Any], action: str) -> str:
        parts: list[str] = []
        parts.append("[Contexto narrativo]")

        summary = ctx.get("summary")
        if summary and summary.strip():
            parts.append("\n[Resumo da história]")
            parts.append(summary.strip())

        events = ctx.get("recent_events") or []
        if events:
            parts.append("\n[Eventos recentes]")
            for e in events[-5:]:
                parts.append(f"• {e.strip()}")

        combined = ctx.get("combined_context")
        if combined:
            parts.append("\n[Contexto relevante]")
            for c in combined[:5]:
                parts.append(f"• {c.strip()}")

        vector = ctx.get("vector_context")
        if vector:
            parts.append("\n[Memória relevante]")
            for v in vector[:3]:
                parts.append(f"• {v.strip()}")

        graph = ctx.get("related_entities")
        if graph:
            parts.append("\n[Elementos conectados]")
            parts.append(", ".join(graph[:5]))

        semantic = ctx.get("semantic")
        if semantic and semantic.strip():
            parts.append("\n[Contexto adicional]")
            parts.append(semantic.strip())

        parts.append("\n[Ação do jogador]")
        parts.append(self.normalize_action(action))

        parts.append("\nDescreva o que acontece a seguir.")
        return "\n".join(parts)

    def normalize_action(self, action: str) -> str:
        if not action:
            return ""
        return " ".join(action.strip().split())

    def enforce_length(self, text: str, max_chars: int) -> str:
        if not text:
            return ""
        return text[:max_chars]

    def sanitize_output(self, text: str) -> str:
        if text is None:
            raise ValueError("LLM output cannot be None")

        text = text.strip()
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]

        cleaned = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(cleaned).strip()

    def get_generation_config(self, scene_type: str | None) -> dict[str, Any]:
        configs = {
            "COMBAT": {"temperature": 0.8, "max_tokens": 200},
            "EXPLORATION": {"temperature": 0.6, "max_tokens": 300},
            "SOCIAL": {"temperature": 0.75, "max_tokens": 250},
        }
        return configs.get(scene_type or "", {"temperature": 0.7, "max_tokens": 250})
