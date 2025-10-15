from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.sql import func

from ..database import Base


class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String)
    amount = Column(Float)
    date = Column(DateTime, default=func.now())
