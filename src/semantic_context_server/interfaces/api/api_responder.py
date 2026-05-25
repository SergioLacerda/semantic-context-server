from typing import Any

from fastapi.responses import JSONResponse


class ApiResponder:
    def __init__(self) -> None:
        self.payload: dict[str, Any] | None = None

    async def send(self, content: str) -> None:
        self.payload = {"message": content}

    def response(self) -> JSONResponse:
        return JSONResponse(content=self.payload or {"message": ""})
