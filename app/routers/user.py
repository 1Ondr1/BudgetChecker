from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
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
        return RedirectResponse(url="/auth/login", status_code=303)
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        return HTTPException(status_code=404, detail="User not found")
    return templates.TemplateResponse(
        "user_page.html", {"request": request, "user": user}
    )


@router.delete("/user/{user.id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": f"User {user.login} was deleted"}
