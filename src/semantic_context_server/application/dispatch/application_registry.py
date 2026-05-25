import inspect
import logging
from typing import Any

logger = logging.getLogger(__name__)


class ApplicationRegistry:
    """
    Registro centralizado de Comandos e Queries.
    Centraliza a descoberta sem quebrar a segregação de execução (CQRS).
    """

    def __init__(self) -> None:
        self._commands: dict[str, type] = {}
        self._queries: dict[str, type] = {}
        self._events: dict[str, type] = {}
        self._storage_adapters: dict[str, Any] = {}
        self._subscribers: dict[str, list[type]] = {}

    def register_command(self, name: str, cls: type) -> None:
        self._commands[name] = cls

    def register_query(self, name: str, cls: type) -> None:
        self._queries[name] = cls

    def register_event(self, name: str, cls: type) -> None:
        self._events[name] = cls

    def register_storage(self, name: str, adapter_instance: Any) -> None:
        self._storage_adapters[name] = adapter_instance

    def subscribe(self, event_name: str, handler_cls: type) -> None:
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        self._subscribers[event_name].append(handler_cls)

    def get_all_subscribers(self) -> dict[str, list[type]]:
        """
        Retorna o mapa completo de inscrições para o bootstrap do EventBus.
        """
        return self._subscribers

    def configure(self, container: Any) -> None:
        """
        Orquestra a fiação (wiring) de comandos e handlers globais.
        """
        logger.info("ApplicationRegistry: wiring global administrative handlers")

        # Exemplo de wiring administrativo:
        # No futuro, importe os comandos administrativos aqui
        # bus.register(
        #     CreateCampaignCommand,
        #     container.create_campaign,
        #     name="create_campaign"
        # )

        logger.debug("Global CommandBus wiring completed")

    def get_command(self, name: str) -> type | None:
        return self._commands.get(name)

    def get_query(self, name: str) -> type | None:
        return self._queries.get(name)

    def get_event(self, name: str) -> type | None:
        return self._events.get(name)

    def validate(self) -> None:
        """
        Verifica se todos os comandos, queries e eventos registrados seguem
        os padrões de assinatura e o Async Mandate.
        """
        errors: list[str] = []
        self._validate_command_handlers(errors)
        self._validate_storage_adapters(errors)
        self._validate_subscribers(errors)
        if errors:
            raise TypeError("Falha na validação do ApplicationRegistry:\n" + "\n".join(errors))

    def _is_async(self, target: Any) -> bool:
        return inspect.iscoroutinefunction(target) or inspect.isasyncgenfunction(target)

    def _validate_command_handlers(self, errors: list[str]) -> None:
        for category, items in [("Command", self._commands), ("Query", self._queries)]:
            for name, cls in items.items():
                target = getattr(cls, "handle", cls if callable(cls) else None)
                if target and not self._is_async(target):
                    errors.append(
                        f"[Async Mandate Error] {category} '{name}' ({cls.__name__}): o método handle ou __call__ deve ser 'async def'."
                    )

    def _validate_storage_adapters(self, errors: list[str]) -> None:
        for name, adapter in self._storage_adapters.items():
            for attr_name in dir(adapter):
                if attr_name.startswith("_"):
                    continue
                method = getattr(adapter, attr_name)
                if callable(method) and not self._is_async(method):
                    errors.append(
                        f"[Async Mandate Error] Storage Adapter '{name}': método público '{attr_name}' violou a governança e deve ser 'async def'."
                    )

    def _validate_subscribers(self, errors: list[str]) -> None:
        for _event_name, handler_classes in self._subscribers.items():
            for h_cls in handler_classes:
                self._validate_handler_cls(h_cls, errors)

    def _validate_handler_cls(self, h_cls: type, errors: list) -> None:
        target = getattr(h_cls, "handle", h_cls if callable(h_cls) else None)
        if not target:
            errors.append(
                f"Handler '{h_cls.__name__}' deve implementar o método 'handle' ou ser chamável."
            )
            return
        if not self._is_async(target):
            errors.append(
                f"Handler '{h_cls.__name__}' violou o Async Mandate: deve ser 'async def'."
            )
        sig = inspect.signature(target)
        params = [p for p in sig.parameters.values() if p.name not in ("self", "cls")]
        if len(params) != 2:
            errors.append(
                f"Handler '{h_cls.__name__}' possui assinatura inválida: esperado (bus, event), obtido {sig}"
            )

    def resolve_query(self, name: str, args: list[str] | None = None) -> type | None:
        """
        Resolve queries simples ou compostas (ex: campaign:list).
        """
        # Caso simples
        if name in self._queries:
            return self._queries[name]

        # Caso composto
        if args:
            composed = f"{name}:{args[0]}"
            return self._queries.get(composed)

        return None

    def list_commands_meta(self) -> list[dict[str, Any]]:
        """
        Retorna metadados para geração de ajuda (DRY).
        """
        result = []
        # Ordena por categoria se disponível, ou por nome
        sorted_cmds = sorted(
            self._commands.items(), key=lambda x: (getattr(x[1], "category", "Outros"), x[0])
        )

        for name, cls in sorted_cmds:
            result.append(
                {
                    "name": name,
                    "usage": getattr(cls, "usage", name),
                    "description": getattr(cls, "description", ""),
                    "category": getattr(cls, "category", "Outros"),
                }
            )

        return result

    def list_events_meta(self) -> list[dict[str, Any]]:
        """
        Retorna metadados dos eventos para documentação técnica.
        """
        result = []
        for name, cls in sorted(self._events.items()):
            subscribers = self._subscribers.get(name, [])
            result.append(
                {
                    "name": name,
                    "class": cls.__name__,
                    "description": getattr(cls, "description", ""),
                    "subscribers": [s.__name__ for s in subscribers],
                }
            )
        return result
