# TODO Сделать фильтрацию, добавление, удаление и редактирование затрат
from fastapi import Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from ..config import templates
from ..database import get_db
from ..models.expense import Expense
from ..services.user_services import get_current_user

router = APIRouter(prefix="/expenses", tags={"expenses"})


@router.get("/", response_class=HTMLResponse)
def get_expenses(
    request: Request,
    current_user: Session = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user == 401:
        return RedirectResponse(url="/auth/login", status_code=303)
    expenses = (
        db.query(Expense)
        .filter(Expense.user_id == current_user["user_id"])
        .order_by(Expense.date.desc())
        .all()
    )
    return templates.TemplateResponse(
        "expenses.html", {"request": request, "expenses": expenses}
    )


@router.get("/", response_class=HTMLResponse)
def show_expenses(request: Request):
    return templates.TemplateResponse("expenses.html", {"request": request})
