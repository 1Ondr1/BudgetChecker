import base64
import io
from datetime import datetime

import matplotlib.pyplot as plt
from sqlalchemy.orm import Session
from sqlalchemy.sql import desc, func

from ..models.category import Category
from ..models.expense import Expense


def get_monthly_expenses(user_id: str, month_from: str, month_to: str, db: Session):
    if not month_from and not month_to:
        return []
    date_group = func.date_trunc("month", Expense.date)
    expenses = (
        db.query(
            date_group.label("month"),
            func.sum(Expense.amount).label("total_amount"),
        )
        .filter(Expense.user_id == user_id)
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
    expenses = expenses.order_by(desc("month")).all()
    return expenses


def get_category_expenses(user_id: str, month_from: str, month_to: str, db: Session):
    if not month_from and not month_to:
        return []
    expenses = (
        db.query(
            Category.name.label("category"),
            func.sum(Expense.amount).label("total_amount"),
        )
        .join(Category, Expense.category_id == Category.id)
        .filter(Expense.user_id == user_id)
        .group_by(Category.name)
    )
    if month_from:
        expenses = expenses.filter(
            Expense.date >= datetime.strptime(month_from, "%Y-%m").date()
        )
    if month_to:
        expenses = expenses.filter(
            Expense.date <= datetime.strptime(month_to, "%Y-%m").date()
        )
    expenses = expenses.order_by(desc(Category.name)).all()
    return expenses


def build_monthly_chart(expenses: Expense):
    if not expenses:
        return None
    months = [e.month.strftime("%Y-%m") for e in expenses]
    totals = [e.total_amount for e in expenses]

    plt.figure(figsize=(7, 4))
    plt.plot(months, totals, marker="o", color="#2563eb")
    plt.title("Динамика расходов по месяцам", fontsize=12)
    plt.xlabel("Месяц")
    plt.ylabel("Сумма расходов, грн")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.xticks(rotation=60, ha="right")
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def build_category_chart(expenses: Expense):
    if not expenses:
        return None

    labels = [e.category for e in expenses]
    amounts = [e.total_amount for e in expenses]

    plt.figure(figsize=(6, 6))
    plt.pie(
        amounts,
        labels=labels,
        autopct="%1.1f%%",
        startangle=140,
        wedgeprops={"edgecolor": "white"},
    )
    plt.title("Распределение расходов по категориям", fontsize=12)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")
