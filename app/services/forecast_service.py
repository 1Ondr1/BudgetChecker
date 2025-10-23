# from fastapi import Depends


from datetime import datetime

from dateutil.relativedelta import relativedelta

from ..models.expense import Expense
from ..schemes.forecast import MonthlyForecast


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
