from sqlalchemy.orm import Session
from sqlalchemy.sql import desc

from ..models.category import Category
from ..models.expense import Expense


def get_expenses(
    user_id: str,
    date_from: str | None,
    date_to: str | None,
    category: str | None,
    db: Session,
):
    categories = db.query(Category).all()
    expenses = db.query(Expense).filter(Expense.user_id == user_id)
    if date_from:
        expenses = expenses.filter(Expense.date >= date_from).od
    if date_to:
        expenses = expenses.filter(Expense.date <= date_to)
    if category:
        expenses = expenses.filter(Expense.category.has(Category.name == category))
    expenses = expenses.order_by(desc(Expense.date)).all()
    return expenses, categories


def add_new_expense(
    user_id: int, category: int, amount: float, date: str | None, db: Session
):
    expense = Expense(user_id=user_id, category_id=category, amount=amount, date=date)
    print(expense.amount)
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


def delete_expense(expense_id: int, db: Session):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    db.delete(expense)
    db.commit()
