from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from ..config import templates
from ..database import get_db
from ..services.user_services import check_user, delete_user, get_current_user

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/home", response_class=HTMLResponse)
def user_page(
    request: Request,
    current_user: Session = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user == 401:
        return RedirectResponse(url="/auth/login", status_code=303)
    user = check_user(current_user["user_id"], db)
    if not user:
        return HTTPException(status_code=404, detail="Користувача не знайдено")
    return templates.TemplateResponse(
        "user_page.html", {"request": request, "user": user}
    )


@router.delete("/user/{user.id}")
def delete(user_id: int, db: Session = Depends(get_db)):
    user = delete_user(user_id=user_id, db=db)
    return {"message": f"Користувач {user.login} був видалений"}
