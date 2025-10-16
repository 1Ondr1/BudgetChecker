# TODO доделать
from sqlalchemy.orm import Session

from ..models.user import User
from ..utils.hashing import hash_password, verify_password


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
