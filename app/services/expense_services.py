from sqlalchemy.orm import Session

from ..models.expense import Expense


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
