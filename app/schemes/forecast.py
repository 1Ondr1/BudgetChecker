from datetime import datetime

from pydantic import BaseModel


class Forecast(BaseModel):
    month: datetime
    total: float | None = None
    predicted: float | None = None
