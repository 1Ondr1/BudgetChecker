from datetime import datetime

from fastapi import Depends, Query
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from ..config import templates
from ..database import get_db
from ..services.forecast_service import get_linear_forecast
from ..services.user_services import get_current_user

router = APIRouter(prefix="/forecast", tags=["forecast"])


@router.get("/", response_class=HTMLResponse)
def show_page(request: Request):
    return templates.TemplateResponse("forecast.html", {"request": request})


# TODO Начать делать следующий алгоритм и сделать нормальные данные для рассходов в бд
@router.get("/linear", response_class=HTMLResponse)
def linear_forecast(
    request: Request,
    current_user: Session = Depends(get_current_user),
    month_from: str = Query(None),
    month_to: str = Query(None),
    window: int = Query(3),
    predict_months: int = Query(1),
    db: Session = Depends(get_db),
):
    forecast = get_linear_forecast(
        user_id=current_user["user_id"],
        month_from=month_from,
        month_to=month_to,
        predict_months=predict_months,
        window=window,
        db=db,
    )
    months = []
    actual_values = []
    linear_predicted = []
    for val in forecast:
        months.append(datetime.strftime(val.month, "%Y-%m"))
        actual_values.append(val.total)
        linear_predicted.append(val.predicted)
    return templates.TemplateResponse(
        "forecast.html",
        {
            "request": request,
            "months": months,
            "forecast_linear": forecast,
            "actual_values": actual_values,
            "linear_predicted": linear_predicted,
            "month_from": month_from,
            "month_to": month_to,
            "predict_months": predict_months,
            "window": window,
        },
    )
