class ContextOrchestrator:
    def __init__(self, *, max_chars: int = 1200):
        self.max_chars = max_chars

    # ---------------------------------------------------------

    def build(self, ctx: dict, action: str) -> str:
        """
        Constrói contexto final com:
        - prioridade
        - limite
        - pruning
        """

        blocks: list[str] = []
        size = 0

        def add_block(title: str, content: str) -> None:
            nonlocal size

            if not content:
                return

            block = f"{title}:\n{content.strip()}\n"

            if size + len(block) > self.max_chars:
                return

            blocks.append(block)
            size += len(block)

        # -----------------------------------------------------
        # 1. RECENT EVENTS (🔥 MAIS IMPORTANTE)
        # -----------------------------------------------------
        recent = ctx.get("recent_events") or []
        if recent:
            text = "\n".join(f"- {e}" for e in recent if e)
            add_block("Eventos recentes", text)

        # -----------------------------------------------------
        # 2. RETRIEVED CONTEXT
        # -----------------------------------------------------
        retrieved = ctx.get("retrieved") or ""
        if retrieved:
            add_block("Contexto relevante", retrieved)

        # -----------------------------------------------------
        # 3. SUMMARY
        # -----------------------------------------------------
        summary = ctx.get("summary") or ""
        if summary:
            add_block("Resumo da campanha", summary)

        # -----------------------------------------------------
        # 4. ENTITIES
        # -----------------------------------------------------
        entities = ctx.get("entities") or []
        if entities:
            add_block("Entidades", ", ".join(entities))

        # -----------------------------------------------------
        # FINAL PROMPT
        # -----------------------------------------------------
        blocks.append(f"Ação do jogador:\n{action}")
        blocks.append("Continue a narrativa.")

        return "\n".join(blocks).strip()
