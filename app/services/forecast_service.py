# from fastapi import Depends


from datetime import datetime

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sqlalchemy.orm import Session

from ..models.expense import Expense
from ..schemes.forecast import Forecast, MonthlyForecast
from ..services.analytics_service import get_monthly_expenses


def data_prepearing(
    user_id: int, month_from: str, month_to: str, predict_months: int, db: Session
):
    expenses = get_monthly_expenses(
        user_id=user_id, month_from=month_from, month_to=month_to, db=db
    )
    months = [val.month.strftime("%Y-%m") for val in expenses]
    amounts = [val.total_amount for val in expenses]
    return months, amounts


def get_linear_forecast(
    user_id: int, month_from: str, month_to: str, predict_months: int, db: Session
):
    expenses = get_monthly_expenses(
        user_id=user_id, month_from=month_from, month_to=month_to, db=db
    )
    df = pd.DataFrame(expenses, columns=["month", "total"])
    df["month"] = pd.to_datetime(df["month"])
    df = df.set_index("month").sort_index()
    df = df.asfreq("MS", fill_value=0)
    x = np.arange(len(df)).reshape(-1, 1)
    y = df["total"].values
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, train_size=0.2, shuffle=False
    )
    model = LinearRegression()
    model.fit(x_train, y_train)
    future_x = np.arange(len(df), len(df) + predict_months).reshape(-1, 1)
    prediction = model.predict(future_x)
    # TODO Сделать нормальный вывод данных через схему Forecast
    predicted_expenses = [
        Forecast(val.month, val.total_amount, None) for val in expenses
    ]
    predicted_expenses.append(Forecast(predict_months))
    print(prediction)
    return prediction


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
            MonthlyForecast(
                month=expenses[val].month,
                total="{:.2f}".format(expenses[val].total_amount),
            )
        )
        predict += expenses[val].total_amount
    for i in range(window, len(expenses)):
        forecast.append(
            MonthlyForecast(
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
            MonthlyForecast(
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
