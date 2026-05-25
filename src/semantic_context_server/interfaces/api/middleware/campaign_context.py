# interfaces/api/middleware/campaign_context.py
from typing import Any

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class CampaignContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Any, call_next: Any) -> Any:
        campaign_id = request.headers.get("X-Campaign-ID") or request.query_params.get(
            "campaign_id"
        )

        if not campaign_id:
            return JSONResponse(
                {"error": "campaign_id is required"},
                status_code=400,
            )

        request.state.campaign_id = campaign_id

        return await call_next(request)
