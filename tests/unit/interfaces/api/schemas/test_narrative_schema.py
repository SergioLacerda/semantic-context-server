import pytest
from pydantic import ValidationError

from semantic_context_server.interfaces.api.schemas.narrative_schema import (
    NarrativeEventRequest,
)


# -----------------------------
# ✅ CASO FELIZ
# -----------------------------
def test_valid_narrative_request():
    data = {"action": "Ataco o goblin", "user_id": "user_123"}

    req = NarrativeEventRequest(**data)

    assert req.action == "Ataco o goblin"
    assert req.user_id == "user_123"


# -----------------------------
# ❌ ACTION VAZIA
# -----------------------------
def test_action_empty_should_fail():
    with pytest.raises(ValidationError):
        NarrativeEventRequest(action="", user_id="user_123")


# -----------------------------
# ❌ ACTION MUITO LONGA
# -----------------------------
def test_action_too_long_should_fail():
    with pytest.raises(ValidationError):
        NarrativeEventRequest(action="a" * 501, user_id="user_123")


# -----------------------------
# ❌ USER_ID AUSENTE
# -----------------------------
def test_user_id_missing_should_fail():
    with pytest.raises(ValidationError):
        NarrativeEventRequest(action="Ataco")


# -----------------------------
# ❌ ACTION AUSENTE
# -----------------------------
def test_action_missing_should_fail():
    with pytest.raises(ValidationError):
        NarrativeEventRequest(user_id="user_123")


def test_invalid_types():
    with pytest.raises(ValidationError):
        NarrativeEventRequest(action=123, user_id=None)  # inválido
