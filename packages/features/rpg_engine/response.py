from dataclasses import dataclass


@dataclass
class Response:
    text: str
    type: str = "text"
    metadata: dict | None = None
