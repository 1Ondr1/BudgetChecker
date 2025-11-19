from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    amount = Column(Float, nullable=False)
    date = Column(DateTime, default=func.now())

    category = relationship("Category")
