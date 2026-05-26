from __future__ import annotations


class SessionSummarizer:
    """Core summarizer prompt utilities for end-session workflows."""

    def extract(self, events: list[dict]) -> str:
        if not events:
            return ""

        lines = []
        for e in events:
            text = (e.get("text") or "").strip()
            role = (e.get("type") or "").upper()

            if not text or len(text) < 5:
                continue

            if role == "USER":
                lines.append(f"[Jogador] {text}")
            elif role == "GM":
                lines.append(f"[Mestre] {text}")
            else:
                lines.append(text)

        return "\n".join(lines[-20:])

    def build_prompt(self, text: str) -> str:
        if not text:
            return ""

        return f"""
Você é um narrador experiente de RPG.

Sua tarefa é condensar a sessão em um resumo narrativo de alta qualidade.

REGRAS:
- Preserve eventos importantes
- Mantenha ordem cronológica
- Destaque decisões do jogador
- Destaque mudanças no mundo
- Remova detalhes irrelevantes
- Seja conciso (2–3 parágrafos)

ESTRUTURA:
- Situação inicial
- Principais eventos
- Consequências

SESSÃO:
{text}

RESUMO:
""".strip()
