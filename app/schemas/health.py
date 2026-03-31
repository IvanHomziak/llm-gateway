from typing import Literal
from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: Literal["ok", "error"] = "ok"
    app_name: str
    version: str
    provider: str