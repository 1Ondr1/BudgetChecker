from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    login: str
    password: str
    email: EmailStr


class UserLogin(BaseModel):
    login: str
    password: str


class UserResponse(BaseModel):
    id: int
    login: str
    email: EmailStr
    create_date: datetime

    class Config:
        orm_mode = True
