from typing import Optional

from fastapi import Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from ..config import templates
from ..database import get_db
from ..models.category import Category
from ..schemes.expense import ExpenseResponse
from ..services.expense_services import add_new_expense, delete_expense, get_expenses
from ..services.user_services import get_current_user

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.get("/", response_class=HTMLResponse)
def show_expenses(
    request: Request,
    current_user: Session = Depends(get_current_user),
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    category: Optional[str] = None,
    ai_category_result: Optional[str] = None,
    db: Session = Depends(get_db),
):
    if current_user == 401:
        return RedirectResponse(url="/auth/login", status_code=303)
    expenses, categories = get_expenses(
        user_id=current_user["user_id"],
        date_from=date_from,
        date_to=date_to,
        category=category,
        db=db,
    )
    return templates.TemplateResponse(
        "expenses.html",
        {
            "request": request,
            "expenses": expenses,
            "categories": categories,
            "date_from": date_from,
            "date_to": date_to,
            "category": category,
            "ai_category_result": ai_category_result,
        },
    )


# TODO Додалать это
@router.post("/add_expense")
def add_expense(
    category_mode: str = Form(...),
    category_select: Optional[int] = Form(None),
    category_text: Optional[str] = Form(None),
    amount: float = Form(...),
    date: Optional[str] = Form(None),
    current_user: Session = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None,
):
    if current_user == 401:
        return RedirectResponse(url="/auth/login", status_code=303)

    if category_mode == "list":
        category = category_select
    else:
        if not category_text or category_text.strip() == "":
            return templates.TemplateResponse(
                "expenses.html",
                {"request": request, "error": "Введите категорию вручную"},
            )
        user_text = category_text.strip()
        ai_result = user_text  # change
        category = (
            db.query(Category)
            .filter(
                Category.user_id == current_user["user_id"], Category.name == ai_result
            )
            .first()
        )
        if not category:
            category = Category(user_id=current_user["user_id"], name=ai_result)
            db.add(category)
            db.commit()
            db.refresh(category)
        category_id = category.id
    expense = add_new_expense(
        user_id=current_user["user_id"],
        category=category_id,
        amount=amount,
        date=None if not date else date,
        db=db,
    )
    if not expense:
        raise HTTPException(status_code=404, detail="Error")
    ExpenseResponse.model_validate(expense)
    if category_mode == "text":
        expenses, categories = get_expenses(
            user_id=current_user["user_id"],
            date_from=None,
            date_to=None,
            category=None,
            db=db,
        )
        return templates.TemplateResponse(
            "expenses.html",
            {
                "request": request,
                "expenses": expenses,
                "categories": categories,
                "ai_category_result": ai_result,
            },
        )
    return RedirectResponse("/expenses", status_code=303)


@router.post("/delete_expense")
def delete(expense_id: int = Form(...), db: Session = Depends(get_db)):
    delete_expense(expense_id=expense_id, db=db)
    return RedirectResponse("/expenses", status_code=303)
