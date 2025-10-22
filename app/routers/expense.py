from typing import Optional

from fastapi import Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from ..config import templates
from ..database import get_db
from ..models.category import Category
from ..models.expense import Expense
from ..schemes.expense import ExpenseResponse
from ..services.expense_services import add_new_expense, delete_expense
from ..services.user_services import get_current_user

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.get("/", response_class=HTMLResponse)
def get_expenses(
    request: Request,
    current_user: Session = Depends(get_current_user),
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    if current_user == 401:
        return RedirectResponse(url="/auth/login", status_code=303)
    categories = db.query(Category).all()
    expenses = db.query(Expense).filter(Expense.user_id == current_user["user_id"])
    if date_from:
        expenses = expenses.filter(Expense.date >= date_from)
    if date_to:
        expenses = expenses.filter(Expense.date <= date_to)
    if category:
        expenses = expenses.filter(Expense.category.has(Category.name == category))
    expenses = expenses.all()
    return templates.TemplateResponse(
        "expenses.html",
        {
            "request": request,
            "expenses": expenses,
            "categories": categories,
            "date_from": date_from,
            "date_to": date_to,
            "category": category,
        },
    )


@router.post("/add_expense")
def add_expense(
    category: int = Form(...),
    amount: float = Form(...),
    date: Optional[str] = Form(None),
    current_user: Session = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user == 401:
        return RedirectResponse(url="/auth/login", status_code=303)
    expense = add_new_expense(
        user_id=current_user["user_id"],
        category=category,
        amount=amount,
        date=None if not date else date,
        db=db,
    )
    if not expense:
        raise HTTPException(status_code=404, detail="Error")
    ExpenseResponse.model_validate(expense)
    return RedirectResponse("/expenses", status_code=303)


@router.post("/delete_expense")
def delete(expense_id: int = Form(...), db: Session = Depends(get_db)):
    delete_expense(expense_id=expense_id, db=db)
    return RedirectResponse("/expenses", status_code=303)
