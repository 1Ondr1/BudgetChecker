from datetime import datetime

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta
from sklearn.linear_model import LinearRegression
from sqlalchemy.orm import Session
from statsmodels.tsa.arima.model import ARIMA

from ..models.expense import Expense
from ..schemes.forecast import Forecast
from ..services.analytics_service import get_monthly_expenses


def get_linear_forecast(
    user_id: int,
    month_from: str,
    month_to: str,
    predicted_months: int,
    window: int,
    db: Session,
):
    expenses = get_monthly_expenses(
        user_id=user_id, month_from=month_from, month_to=month_to, db=db
    )
    if not expenses:
        return []
    df = pd.DataFrame(expenses, columns=["month", "total"])
    df["month"] = pd.to_datetime(df["month"])
    df = df.set_index("month").sort_index()
    df = df.asfreq("MS", fill_value=0)
    df["smooth"] = df["total"].rolling(window=3, min_periods=1).mean()
    total = df["smooth"].values
    if len(df) < window + 1:
        return []
    if len(df) <= window:
        window = min(window, len(df) - 1)
    x, y = [], []
    for i in range(len(df) - window):
        x.append(total[i : i + window])
        y.append(total[i + window])
    x, y = np.array(x), np.array(y)
    model = LinearRegression()
    model.fit(x, y)
    prediction = []
    total_copy = total.copy()
    avg = np.mean(total)
    std = np.std(total)
    for _ in range(predicted_months):
        future_x = np.array(total_copy[-window:]).reshape(1, -1)
        temp_predict = model.predict(future_x)
        upper_limit = avg + 2.5 * std
        lower_limit = max(0, avg - 2.5 * std)
        temp_predict = min(max(temp_predict, lower_limit), upper_limit)
        temp_predict *= np.random.uniform(0.95, 1.05)
        prediction = np.append(prediction, temp_predict)
        total_copy = np.append(total_copy, temp_predict)
    expenses_period = get_monthly_expenses(
        user_id=user_id,
        month_from=month_from,
        month_to=datetime.strftime(
            datetime.strptime(month_to, "%Y-%m")
            + relativedelta(months=predicted_months),
            "%Y-%m",
        ),
        db=db,
    )
    expenses_dict = {k.date(): v for k, v in expenses_period}
    predicted_expenses = []
    for month, row in df.iterrows():
        predicted_expenses.append(
            {
                "month": datetime.strftime(month.to_pydatetime(), "%Y-%m"),
                "total": float(row["total"]),
                "predicted": None,
            }
        )

    current_month = datetime.strptime(month_to, "%Y-%m") + relativedelta(months=1)
    for value in prediction:
        total_value = expenses_dict.get(current_month.date())
        predicted_expenses.append(
            {
                "month": datetime.strftime(current_month, "%Y-%m"),
                "total": float(total_value) if total_value else None,
                "predicted": float(value),
            }
        )
        current_month += relativedelta(months=1)

    return predicted_expenses


def get_arima_forecast(
    user_id: int,
    month_from: str,
    month_to: str,
    predicted_months: int,
    window: int,
    db: Session,
):
    expenses = get_monthly_expenses(
        user_id=user_id, month_from=month_from, month_to=month_to, db=db
    )

    if not expenses:
        return [], True

    df = pd.DataFrame(expenses, columns=["months", "total"])
    df["months"] = pd.to_datetime(df["months"])
    df = df.set_index("months").sort_index().asfreq("MS", fill_value=0)
    df["smooth"] = df["total"].rolling(window=3, min_periods=1).mean()

    order_candidates = [(window, 1, 1), (window, 1, 2)]
    fitted = False
    used_fallback = False

    for order in order_candidates:
        try:
            model = ARIMA(df["total"], order=order, trend="n")
            model_fit = model.fit()
            fitted = True
            break
        except Exception:
            continue

    if fitted:
        prediction = model_fit.forecast(steps=predicted_months)
        prediction = np.clip(
            prediction,
            df["total"].min() * 0.9,
            df["total"].max() * 1.1,
        )
    else:
        used_fallback = True
        mean_value = float(df["total"].mean())
        prediction = [mean_value] * predicted_months

    predicted_expenses = []

    expenses_period = get_monthly_expenses(
        user_id=user_id,
        month_from=month_from,
        month_to=datetime.strftime(
            datetime.strptime(month_to, "%Y-%m")
            + relativedelta(months=predicted_months),
            "%Y-%m",
        ),
        db=db,
    )
    expenses_dict = {k.date(): v for k, v in expenses_period}
    for month, value in df.iterrows():
        predicted_expenses.append(
            {
                "month": datetime.strftime(month, "%Y-%m"),
                "total": value["total"],
                "predicted": None,
            }
        )
    current_month = datetime.strptime(month_to, "%Y-%m") + relativedelta(months=1)
    for value in prediction:
        total_value = expenses_dict.get(current_month.date())
        predicted_expenses.append(
            {
                "month": datetime.strftime(current_month, "%Y-%m"),
                "total": float(total_value) if total_value else None,
                "predicted": float(value),
            }
        )
        current_month += relativedelta(months=1)

    return predicted_expenses, used_fallback


def monthly_forecast(
    expenses: Expense,
    window: int,
    month_to: str | None,
):
    predict = 0
    month = expenses[-1].month
    month_to = datetime.strptime(month_to, "%Y-%m")
    last_amount = expenses[0].total_amount
    forecast = []
    for val in range(window):
        forecast.append(
            Forecast(
                month=expenses[val].month,
                total="{:.2f}".format(expenses[val].total_amount),
            )
        )
        predict += expenses[val].total_amount
    for i in range(window, len(expenses)):
        forecast.append(
            Forecast(
                month=expenses[i].month,
                total="{:.2f}".format(expenses[i].total_amount),
                predicted="{:.2f}".format(predict / window),
            )
        )
        predict = predict + expenses[i].total_amount - last_amount
        last_amount = expenses[i - window].total_amount
    while month != month_to:
        month += relativedelta(months=1)
        print(predict)
        print(last_amount)
        forecast.append(
            Forecast(
                month=month, total=None, predicted="{:.2f}".format(predict / window)
            )
        )
        predict = predict + forecast[-1].predicted - last_amount
        if forecast[len(forecast) - window].total:
            last_amount = forecast[len(forecast) - window].total
        else:
            last_amount = forecast[len(forecast) - window].predicted
    return forecast
    return forecast
