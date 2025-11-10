from datetime import datetime

from fastapi import Depends, Query
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from ..config import templates
from ..database import get_db
from ..services.forecast_service import (
    get_arima_forecast,
    get_linear_forecast,
    get_mlp_forecast,
)
from ..services.user_services import get_current_user

router = APIRouter(prefix="/forecast", tags=["forecast"])


@router.get("/", response_class=HTMLResponse)
def show_page(request: Request):
    return templates.TemplateResponse("forecast.html", {"request": request})


# TODO Начать делать следующий алгоритм и сделать нормальные данные для рассходов в бд
@router.get("/linear")
def linear_forecast(
    current_user: Session = Depends(get_current_user),
    month_from: str = Query(None),
    month_to: str = Query(None),
    window: int = 6,
    predict_months: int = Query(1),
    db: Session = Depends(get_db),
):
    if month_from and month_to:
        diff_months = (
            datetime.strptime(month_to, "%Y-%m")
            - datetime.strptime(month_from, "%Y-%m")
        ).days // 30
        if diff_months < 6:
            return JSONResponse(
                {
                    "error": "Період повинен бути не менше 6 місяців для побудови прогнозу.",
                    "month_from": month_from,
                    "month_to": month_to,
                    "predict_months": predict_months,
                },
                status_code=400,
            )
    forecast = get_linear_forecast(
        user_id=current_user["user_id"],
        month_from=month_from,
        month_to=month_to,
        predict_months=predict_months,
        window=window,
        db=db,
    )
    months = [f["month"] for f in forecast]
    actual_values = [f["total"] for f in forecast]
    linear_predicted = [f["predicted"] for f in forecast]
    return JSONResponse(
        {
            "months": months,
            "forecast_linear": forecast,
            "actual_values": actual_values,
            "linear_predicted": linear_predicted,
            "error": None,
        },
    )


@router.get("/arima")
def arima_forecast(
    current_user: Session = Depends(get_current_user),
    month_from: str = Query(None),
    month_to: str = Query(None),
    window: int = Query(None),
    predict_months: int = Query(1),
    db: Session = Depends(get_db),
):
    if month_from and month_to:
        diff_months = (
            datetime.strptime(month_to, "%Y-%m")
            - datetime.strptime(month_from, "%Y-%m")
        ).days // 30
        if diff_months < 6:
            return JSONResponse(
                {
                    "error": "Період повинен бути не менше 6 місяців для побудови прогнозу.",
                },
                status_code=400,
            )
    forecast, used_fallback = get_arima_forecast(
        user_id=current_user["user_id"],
        month_from=month_from,
        month_to=month_to,
        window=window,
        predicted_months=predict_months,
        db=db,
    )
    months = [f["month"] for f in forecast]
    actual_values = [f["total"] for f in forecast]
    arima_predicted = [f["predicted"] for f in forecast]
    return JSONResponse(
        {
            "months": months,
            "forecast_arima": forecast,
            "actual_values": actual_values,
            "arima_predicted": arima_predicted,
            "used_fallback": used_fallback,
            "error": None,
        }
    )


@router.get("/mlp")
def mlp_forecast(
    current_user: Session = Depends(get_current_user),
    month_from: str = Query(None),
    month_to: str = Query(None),
    window: int = Query(None),
    predict_months: int = Query(1),
    db: Session = Depends(get_db),
):
    if month_from and month_to:
        diff_months = (
            datetime.strptime(month_to, "%Y-%m")
            - datetime.strptime(month_from, "%Y-%m")
        ).days // 30
        if diff_months < 6:
            return JSONResponse(
                {
                    "error": "Період повинен бути не менше 6 місяців для побудови прогнозу.",
                },
                status_code=400,
            )
    forecast = get_mlp_forecast(
        user_id=current_user["user_id"],
        month_from=month_from,
        month_to=month_to,
        predicted_months=predict_months,
        db=db,
    )
    months = [f["month"] for f in forecast]
    actual_values = [f["total"] for f in forecast]
    mlp_predicted = [f["predicted"] for f in forecast]
    return JSONResponse(
        {
            "months": months,
            "forecast_mlp": forecast,
            "actual_values": actual_values,
            "mlp_predicted": mlp_predicted,
            "error": None,
        }
    )
