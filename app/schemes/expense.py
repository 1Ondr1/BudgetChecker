from datetime import datetime

from pydantic import BaseModel, ConfigDict

from .category import CategoryBase


class ExpenseBase(BaseModel):
    user_id: int
    category: CategoryBase
    amount: float


class ExpenseCreate(ExpenseBase):
    date: datetime | None = None


class ExpenseResponse(ExpenseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: datetime
