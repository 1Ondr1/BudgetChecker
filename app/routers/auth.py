from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from ..config import templates
from ..database import get_db
from ..schemes.user import UserResponse
from ..services import user_services
from ..utils.jwt_handler import create_jwt

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(
    login: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
) -> UserResponse:

    user = user_services.create_user(login, email, password, db)
    return UserResponse.model_validate(user)


@router.post("/login")
def login(
    login: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)
) -> UserResponse:
    user = user_services.auth_user(login, password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Wrong password or login")

    token = create_jwt(user)

    response = RedirectResponse(url="/user/home", status_code=303)
    response.set_cookie(
        key="access_token", value=token, httponly=True, max_age=1800, samesite="lax"
    )
    return response


@router.get("/register", response_class=HTMLResponse)
def show_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
def show_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/logout")
def logout_user():
    response = RedirectResponse(url="/auth/login", status_code=303)
    response.delete_cookie("access_token")
    return response
