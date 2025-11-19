from fastapi import Request
from sqlalchemy.orm import Session

from ..config import BASE_CATEGORIES
from ..models.category import Category
from ..models.user import User
from ..utils.hashing import hash_password, verify_password
from ..utils.jwt_handler import verify_jwt


def create_user(login: str, email: str, password: str, db: Session) -> User:
    hashed_pw = hash_password(password)
    user = User(login=login, email=email, password=hashed_pw)
    if (
        db.query(User).filter(User.email.ilike(email)).first()
        or db.query(User).filter(User.login.ilike(login)).first()
    ):
        return None
    db.add(user)
    db.commit()
    db.refresh(user)
    for name in BASE_CATEGORIES:
        db.add(Category(user_id=user.id, name=name))
    db.commit()
    return user


def auth_user(login: str, password: str, db: Session):
    user = db.query(User).filter(User.login.ilike(login)).first()
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return 401

    payload = verify_jwt(token)
    if not payload:
        return 401
    return payload


def check_user(user_id: str, db: Session):
    return db.query(User).filter(User.id == user_id).first()


def delete_user(user_id: int, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    db.delete(user)
    db.commit()
    return user
