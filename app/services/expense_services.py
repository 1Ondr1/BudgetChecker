from sqlalchemy.orm import Session
from sqlalchemy.sql import desc

from ..models.category import Category
from ..models.expense import Expense
from ..services.ai_category_service import predict_category


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
        expenses = expenses.filter(Expense.date >= date_from)
    if date_to:
        expenses = expenses.filter(Expense.date <= date_to)
    if category:
        expenses = expenses.filter(Expense.category.has(Category.name == category))
    expenses = expenses.order_by(desc(Expense.date)).all()
    return expenses, categories


def add_new_expense(
    user_id: int,
    amount: float,
    date: str | None,
    category_mode: str,
    category_select: int | None,
    category_text: str | None,
    db: Session,
):
    if category_mode == "list":
        if not category_select:
            raise ValueError("Оберіть категорію зі списку")
        category_id = category_select
        predicted_label = None
        confidence = None
    else:
        if not category_text or category_text.strip() == "":
            raise ValueError("Введіть категорію")

        text = category_text.strip()
        print(text)

        categories = db.query(Category).all()
        category_map = {c.name: c.id for c in categories}

        predicted_label, confidence = predict_category(text)

        if predicted_label not in category_map or confidence <= 0.20:
            category_id = category_map["Інше"]
        else:
            category_id = category_map[predicted_label]

    expense = Expense(
        user_id=user_id, category_id=category_id, amount=amount, date=date
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense, predicted_label, confidence


def delete_expense(expense_id: int, db: Session):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    db.delete(expense)
    db.commit()
