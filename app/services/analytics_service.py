from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.sql import asc, desc, func

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
    expenses = expenses.order_by(asc("month")).all()
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
