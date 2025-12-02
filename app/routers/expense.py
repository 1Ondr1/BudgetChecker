from typing import Optional
from urllib.parse import quote_plus

from fastapi import Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from ..config import templates
from ..database import get_db
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
    predicted_label: Optional[str] = None,
    confidence: Optional[float] = None,
    error: Optional[str] = None,
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
            "predicted_label": predicted_label,
            "confidence": confidence,
            "error": error,
        },
    )


@router.post("/add_expense")
def add_expense(
    category_mode: str = Form(...),
    category_select: Optional[int] = Form(None),
    category_text: Optional[str] = Form(None),
    amount: float = Form(...),
    date: Optional[str] = Form(None),
    current_user: Session = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user == 401:
        return RedirectResponse(url="/auth/login", status_code=303)
    try:
        expense, predicted_label, confidence = add_new_expense(
            user_id=current_user["user_id"],
            amount=amount,
            date=None if not date else date,
            category_mode=category_mode,
            category_select=category_select,
            category_text=category_text,
            db=db,
        )
    except ValueError as e:
        msg = quote_plus(str(e))
        return RedirectResponse(f"/expenses?error={msg}", status_code=303)
    if not expense:
        raise HTTPException(status_code=404, detail="Error")
    params = []
    if predicted_label:
        params.append(f"predicted_label={quote_plus(predicted_label)}")
    if confidence is not None:
        params.append(f"confidence={confidence:.2f}")

    if predicted_label:
        query_str = "&".join(params)
        redirect_url = "/expenses"
        redirect_url += f"?{query_str}"
        return RedirectResponse(redirect_url, status_code=303)
    ExpenseResponse.model_validate(expense)
    return RedirectResponse("/expenses", status_code=303)


@router.post("/delete_expense")
def delete_expenese_router(expense_id: int = Form(...), db: Session = Depends(get_db)):
    delete_expense(expense_id=expense_id, db=db)
    return RedirectResponse("/expenses", status_code=303)
