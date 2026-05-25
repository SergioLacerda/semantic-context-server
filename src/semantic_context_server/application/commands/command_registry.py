from typing import Any


class CommandRegistry:
    def __init__(self) -> None:
        # --------------------------------------------------
        # Core mappings
        # --------------------------------------------------
        self._handlers: dict[type, Any] = {}
        self._commands_by_name: dict[str, type] = {}

        # --------------------------------------------------
        # Metadata (help, descrição, etc)
        # --------------------------------------------------
        self._meta: dict[type, dict] = {}

    # ======================================================
    # REGISTER
    # ======================================================

    def register(
        self,
        command_type: type,
        handler: Any,
        *,
        name: str | None = None,
        aliases: list[str] | None = None,
        meta: dict | None = None,
    ) -> None:
        """
        Registra um command + handler + metadata

        name:
            Nome principal do comando (ex: "gm", "roll")

        aliases:
            Sinônimos (ex: ["r", "dice"])

        meta:
            Dados para help (usage, description, category, etc)
        """

        # --------------------------------------------------
        # Handler mapping
        # --------------------------------------------------
        if command_type in self._handlers:
            raise RuntimeError(f"Handler already registered for {command_type}")

        self._handlers[command_type] = handler

        # --------------------------------------------------
        # Nome do comando
        # --------------------------------------------------
        resolved_name = name or getattr(command_type, "name", None)

        if resolved_name:
            self._register_name(resolved_name, command_type)

        # --------------------------------------------------
        # Aliases
        # --------------------------------------------------
        if aliases:
            for alias in aliases:
                self._register_name(alias, command_type)

        # --------------------------------------------------
        # Metadata
        # --------------------------------------------------
        final_meta = meta or {}

        # auto-enrichment com atributos da classe
        final_meta.setdefault("name", resolved_name or command_type.__name__)
        final_meta.setdefault("usage", getattr(command_type, "usage", ""))
        final_meta.setdefault("description", getattr(command_type, "description", ""))
        final_meta.setdefault("category", getattr(command_type, "category", "Outros"))

        self._meta[command_type] = final_meta

    # ======================================================
    # INTERNAL HELPERS
    # ======================================================

    def _register_name(self, name: str, command_type: type) -> None:
        key = name.lower()

        if key in self._commands_by_name:
            raise RuntimeError(f"Command name already registered: '{name}'")

        self._commands_by_name[key] = command_type

    # ======================================================
    # RESOLVE (TYPE)
    # ======================================================

    def get(self, command_type: type) -> Any | None:
        """
        Resolve handler por tipo (CommandBus usa isso)
        """
        handler = self._handlers.get(command_type)

        if handler:
            return handler

        # 🔥 fallback por herança (importantíssimo)
        for t, h in self._handlers.items():
            if issubclass(command_type, t):
                return h

        return None

    # ======================================================
    # RESOLVE (NAME)
    # ======================================================

    def get_command(self, name: str) -> type | None:
        """
        Resolve command class por nome (router usa isso)
        """
        if not name:
            return None

        return self._commands_by_name.get(name.lower())

    # ======================================================
    # META / HELP
    # ======================================================

    def get_meta(self, command_type: type) -> dict:
        return self._meta.get(command_type, {})

    def list_meta(self) -> list[dict[str, Any]]:
        return sorted(
            self._meta.values(),
            key=lambda x: (x.get("category", ""), x.get("name", "")),
        )

    # ======================================================
    # DEBUG / INTROSPECTION
    # ======================================================

    def list_commands(self) -> list[str]:
        return list(self._commands_by_name.keys())

    def has(self, command_type: type) -> bool:
        return command_type in self._handlers
