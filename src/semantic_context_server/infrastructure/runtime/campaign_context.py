import contextvars
from collections.abc import Generator
from contextlib import contextmanager

_campaign_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "campaign_id", default=None
)

_UNSET = object()


class CampaignContext:
    """Thread/task-local campaign ID managed via contextvars."""

    def set_campaign(self, campaign_id: str) -> contextvars.Token:
        return _campaign_id_var.set(campaign_id)

    def get_campaign(self) -> str:
        value = _campaign_id_var.get(None)
        if value is None:
            raise RuntimeError(
                "No campaign_id set in current context. "
                "Call set_campaign() or use the scope() context manager first."
            )
        return value

    def reset(self, token: contextvars.Token | None = None) -> None:
        if token is not None:
            _campaign_id_var.reset(token)
        else:
            _campaign_id_var.set(None)

    @contextmanager
    def scope(self, campaign_id: str) -> Generator[str, None, None]:
        token = self.set_campaign(campaign_id)
        try:
            yield campaign_id
        finally:
            _campaign_id_var.reset(token)
