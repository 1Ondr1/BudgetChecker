from datetime import datetime

from fastapi import Depends, Query
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter
from sqlalchemy import asc, func
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
    date_group = func.date_trunc("month", Expense.date)
    expenses = (
        db.query(
            date_group.label("month"),
            func.sum(Expense.amount).label("total_amount"),
        )
        .filter(Expense.user_id == current_user["user_id"])
        .group_by("month")
    )
    if month_from:
        expenses = expenses.filter(
            date_group >= datetime.strptime(month_from, "%Y-%m").date()
        )
    if month_to:
        expenses = expenses.filter(
            date_group <= datetime.strptime(month_to, "%Y-%m").date()
        )
    expenses = expenses.order_by(asc("month")).all()
    forecast = monthly_forecast(expenses=expenses, window=window, month_to=month_to)
    return templates.TemplateResponse(
        "forecast.html", {"request": request, "forecast": forecast}
    )
