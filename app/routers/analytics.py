from fastapi import Depends, Query
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from ..config import templates
from ..database import get_db
from ..services.analytics_service import (
    generate_recommendations,
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
    months = [e.month.strftime("%Y-%m") for e in monthly_expenses]
    totals = [e.total_amount for e in monthly_expenses]
    category_labels = [c.category for c in category_expenses]
    category_values = [c.total_amount for c in category_expenses]
    recommendations = generate_recommendations(
        user_id=current_user["user_id"],
        month_from=month_from,
        month_to=month_to,
        db=db,
    )
    return templates.TemplateResponse(
        "analytics.html",
        {
            "request": request,
            "months": months,
            "totals": totals,
            "category_labels": category_labels,
            "category_values": category_values,
            "monthly_expenses": monthly_expenses,
            "category_expenses": category_expenses,
            "month_to": month_to,
            "month_from": month_from,
            "recommendations": recommendations,
        },
    )
