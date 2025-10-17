import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv

from ..models.user import User

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")


def create_jwt(user: User) -> str:
    payload = {
        "user_id": user.id,
        "login": user.login,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


def verify_jwt(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
