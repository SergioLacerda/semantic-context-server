from typing import Any

from pydantic import BaseModel, Field, field_validator


class NarrativeEventRequest(BaseModel):
    action: str = Field(
        ...,
        max_length=500,
        description="Ação do jogador no RPG",
        examples=["Ataco o goblin com minha espada"],
    )

    user_id: str = Field(
        ...,
        max_length=100,
        description="Identificador do jogador",
        examples=["user_123"],
    )

    # ==========================================================
    # VALIDATION
    # ==========================================================

    @field_validator("action", "user_id")
    @classmethod
    def validate_not_empty(cls, v: str, info: Any) -> str:
        if v is None:
            raise ValueError(f"{info.field_name} is required")

        value = v.strip()

        if not value:
            raise ValueError(f"{info.field_name} must not be empty")

        return value
