from datetime import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl


class MonitorCreate(BaseModel):
    url: HttpUrl
    name: str | None = None


class HealthCheckOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status_code: int | None
    response_time_ms: int | None
    is_up: bool
    error: str | None
    checked_at: datetime


class MonitorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str
    name: str | None
    created_at: datetime
    latest_check: HealthCheckOut | None = None
