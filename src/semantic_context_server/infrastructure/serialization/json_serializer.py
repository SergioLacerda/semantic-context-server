import decimal
from collections.abc import Iterable
from datetime import datetime
from enum import Enum
from typing import Any, TypeVar, cast
from uuid import UUID

T = TypeVar("T")


class JSONSerializer:
    def serialize(self, obj: Any) -> Any:
        """
        Transforma um objeto ou estrutura complexa em um formato
        serializável (dict/list/primários).
        """
        return self._sanitize(obj)

    def deserialize(self, data: Any, cls: type[T]) -> T | None:
        """
        Reconstrói um objeto de classe a partir de dados brutos.
        """
        if data is None:
            return None

        # Suporte a Pydantic (v2)
        if (model_validate := getattr(cls, "model_validate", None)) and callable(model_validate):
            return cast(T, model_validate(data))

        if (from_dict := getattr(cls, "from_dict", None)) and callable(from_dict):
            return cast(T, from_dict(data))

        if isinstance(data, cls):
            return data

        return None

    def _sanitize(self, obj: Any) -> Any:
        if isinstance(obj, (str, int, float, bool)) or obj is None:
            return obj

        if isinstance(obj, datetime):
            return obj.isoformat()

        if isinstance(obj, Enum):
            return obj.value

        if isinstance(obj, (UUID, decimal.Decimal)):
            return str(obj)

        if isinstance(obj, (list, tuple, set, Iterable)) and not isinstance(obj, (str, dict)):
            return [self._sanitize(x) for x in obj]

        if isinstance(obj, dict):
            return {str(k): self._sanitize(v) for k, v in obj.items()}

        # Suporte a Pydantic (model_dump em v2, dict em v1)
        if (model_dump := getattr(obj, "model_dump", None)) and callable(model_dump):
            return self._sanitize(model_dump())

        if (
            (to_dict := getattr(obj, "to_dict", None))
            and callable(to_dict)
            or (to_dict := getattr(obj, "dict", None))
            and callable(to_dict)
        ):
            return self._sanitize(to_dict())

        return str(obj)
