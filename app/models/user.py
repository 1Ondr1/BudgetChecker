from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from ..database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, unique=True)
    password = Column(String)
    email = Column(String, unique=True)
    create_date = Column(DateTime, default=func.now())
