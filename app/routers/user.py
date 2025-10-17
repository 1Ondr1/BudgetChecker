# TODO Сделать нормальный перезод на страницу авторизации, со сменой url
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from ..config import templates
from ..database import get_db
from ..models.user import User
from ..services.user_services import get_current_user

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/home", response_class=HTMLResponse)
def user_page(
    request: Request,
    current_user: Session = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user == 401:
        return templates.TemplateResponse("login.html", {"request": request})
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        return HTTPException(status_code=404, detail="User not found")
    return templates.TemplateResponse(
        "user_page.html", {"request": request, "user": user}
    )
