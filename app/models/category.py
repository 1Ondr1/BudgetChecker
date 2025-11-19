from sqlalchemy import Column, Integer, String, UniqueConstraint

from ..database import Base


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_user_category"),)
