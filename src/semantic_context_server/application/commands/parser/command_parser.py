import shlex
from dataclasses import dataclass


@dataclass
class ParsedCommand:
    name: str
    args: list[str]
    raw: str


class CommandParser:
    def parse(self, input_text: str) -> list[ParsedCommand]:
        if not input_text:
            return []

        raw_text = input_text.strip()

        # ======================================================
        # 🔥 TEXTO LIVRE (SEM COMANDO)
        # ======================================================
        if not raw_text.startswith("!"):
            return [
                ParsedCommand(
                    name="__free_text__",
                    args=[],
                    raw=raw_text,
                )
            ]

        # ======================================================
        # NORMALIZAÇÃO PARA PARSING
        # ======================================================
        normalized = raw_text[1:]

        commands = []

        parts = [p.strip() for p in normalized.split(";") if p.strip()]

        for part in parts:
            try:
                tokens = shlex.split(part)
            except ValueError:
                tokens = part.split()

            if not tokens:
                continue

            name = tokens[0].lower()
            args = tokens[1:]

            commands.append(
                ParsedCommand(
                    name=name,
                    args=args,
                    raw=part,
                )
            )

        return commands
