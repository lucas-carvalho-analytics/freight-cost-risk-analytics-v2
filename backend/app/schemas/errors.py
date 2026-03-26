from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error: str
    message: str
    status_code: int
    details: list[dict[str, object]] | dict[str, object] | None = None
