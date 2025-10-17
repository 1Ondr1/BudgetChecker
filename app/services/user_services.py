from fastapi import HTTPException, Request
from sqlalchemy.orm import Session

from ..models.user import User
from ..utils.hashing import hash_password, verify_password
from ..utils.jwt_handler import verify_jwt


def create_user(login: str, email: str, password: str, db: Session) -> User:
    hashed_pw = hash_password(password)
    user = User(login=login, email=email, password=hashed_pw)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def auth_user(login: str, password: str, db: Session):
    user = db.query(User).filter(User.login == login).first()
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
        raise HTTPException(status_code=401, detail="Bad token")
    return payload
