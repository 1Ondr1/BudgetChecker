# TODO доделать
from fastapi import APIRouter

from ..schemes.user import UserCreate
from ..services import user_services

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(user_create: UserCreate, db):
    user_services.create_user(db, user_create)
