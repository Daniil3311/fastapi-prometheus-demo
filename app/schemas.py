from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ProcessRequest(BaseModel):
    """Validated payload for /process endpoint."""

    model_config = ConfigDict(str_strip_whitespace=True)

    data: str = Field(min_length=1, max_length=500)


class ProcessResponse(BaseModel):
    """Response payload for /process endpoint."""

    echo: str
    processing_seconds: float
