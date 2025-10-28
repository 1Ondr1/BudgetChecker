from fastapi import Depends, Query
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from ..config import templates
from ..database import get_db
from ..services.analytics_service import (
    build_category_chart,
    build_monthly_chart,
    get_category_expenses,
    get_monthly_expenses,
)
from ..services.user_services import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/", response_class=HTMLResponse)
def show_page(
    request: Request,
    current_user: Session = Depends(get_current_user),
    month_from: str = Query(None),
    month_to: str = Query(None),
    db: Session = Depends(get_db),
):
    monthly_expenses = get_monthly_expenses(
        user_id=current_user["user_id"],
        month_from=month_from,
        month_to=month_to,
        db=db,
    )
    category_expenses = get_category_expenses(
        user_id=current_user["user_id"],
        month_from=month_from,
        month_to=month_to,
        db=db,
    )
    monthly_chart = build_monthly_chart(monthly_expenses)
    category_chart = build_category_chart(category_expenses)
    return templates.TemplateResponse(
        "analytics.html",
        {
            "request": request,
            "month_from": month_from,
            "month_to": month_to,
            "monthly_expenses": monthly_expenses,
            "category_expenses": category_expenses,
            "monthly_chart": monthly_chart,
            "category_chart": category_chart,
        },
    )
