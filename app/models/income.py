from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.sql import func

from ..database import Base


class Income(Base):
    __tablename__ = "incomes"
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String)
    amount = Column(Float)
    date = Column(DateTime, default=func.now())
