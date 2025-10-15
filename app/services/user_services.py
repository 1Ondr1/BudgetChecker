# TODO доделать
from ..models.user import User
from ..utils.hashing import hash_password


def create_user(db, user_create):
    hashed_pw = hash_password(user_create.password)
    user = User(login=user_create.login, email=user_create.email, password=hashed_pw)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
