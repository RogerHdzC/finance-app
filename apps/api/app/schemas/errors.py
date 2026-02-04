from __future__ import annotations

from pydantic import BaseModel
from typing import Any

class ErrorResponse(BaseModel):
    code: str
    detail: str
    meta: dict[str, Any] | None = None