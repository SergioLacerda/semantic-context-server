class ContextAssembler:
    def assemble(self, documents: list[str], max_chars: int | None = None) -> str:
        if not documents:
            return ""

        text = "\n\n".join(documents)

        if max_chars:
            return text[:max_chars]

        return text
