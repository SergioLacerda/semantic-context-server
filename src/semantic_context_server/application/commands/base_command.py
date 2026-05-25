from typing import Protocol


class BaseCommand(Protocol):
    """
    Marker base class for CQRS commands (DTO only).

    NÃO contém lógica.
    """

    pass
