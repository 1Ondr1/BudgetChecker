# TODO сделать отделюную структуру для ежемесячных расходов и переделать под это прогнозирование и вывод на странице
from datetime import datetime

from fastapi import Depends, Query
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from ..config import templates
from ..database import get_db
from ..models.expense import Expense
from ..services.forecast_service import monthly_forecast
from ..services.user_services import get_current_user

router = APIRouter(prefix="/forecast", tags=["forecast"])


@router.get("/", response_class=HTMLResponse)
def show_page(request: Request):
    return templates.TemplateResponse("forecast.html", {"request": request})


@router.get("/monthly", response_class=HTMLResponse)
def get_monthly_expenses(
    request: Request,
    current_user: Session = Depends(get_current_user),
    month_from: str = Query(None),
    month_to: str = Query(None),
    window: int = Query(3),
    db: Session = Depends(get_db),
):
    expenses = db.query(Expense).filter(Expense.user_id == current_user["user_id"])
    expenses = expenses.filter(Expense.date >= datetime.strptime(month_from, "%Y-%m"))
    expenses = expenses.filter(Expense.date <= datetime.strptime(month_to, "%Y-%m"))
    expenses = expenses.all()
    forecast = monthly_forecast(expenses=expenses, window=window)
    expenses.append(forecast)
    return templates.TemplateResponse(
        "forecast.html",
        {"request": request, "expenses": expenses},
    )
