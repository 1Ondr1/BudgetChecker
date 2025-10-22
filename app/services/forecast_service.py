# from fastapi import Depends

from dateutil.relativedelta import relativedelta

from ..models.expense import Expense


def monthly_forecast(expenses: Expense, window: int):
    avg = 0
    for i in range(window):
        avg += expenses[-i].amount
    avg /= window
    forecast = Expense(
        user_id=expenses[0].user_id,
        category_id=6,
        amount=avg,
        date=expenses[-1].date + relativedelta(months=1),
    )
    return forecast
