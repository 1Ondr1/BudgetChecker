from datetime import datetime

from pydantic import BaseModel


class IncomeBase(BaseModel):
    source: str
    amount: float


class IncomeCreate(IncomeBase):
    date: datetime | None = None


class IncomeResponse(IncomeBase):
    id: int
    date: datetime

    class Config:
        orm_mode = True
