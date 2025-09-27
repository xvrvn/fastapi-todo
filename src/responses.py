from typing import Any

from pydantic import BaseModel


class APIResponse(BaseModel):
    success: bool
    data: Any | None = None
    message: str | None = None


def success_response(data: Any = None, message: str = "Success") -> dict:
    return APIResponse(success=True, data=data, message=message).model_dump()


def error_response(message: str, status_code: int = 400) -> dict:
    return APIResponse(success=False, data=None, message=message).model_dump()
