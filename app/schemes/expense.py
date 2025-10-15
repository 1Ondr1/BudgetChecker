from datetime import datetime

from pydantic import BaseModel


class ExpenseBase(BaseModel):
    category: str
    amount: float


class ExpenseCreate(ExpenseBase):
    date: datetime | None = None


class ExpenseResponse(ExpenseBase):
    id: int
    date: datetime

    class Config:
        orm_mode = True
