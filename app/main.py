from pathlib import Path

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .models.user import User
from .database import Base, SessionLocal, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_expenses(request: Request, db: Session = Depends(get_db)):
    expenses = db.query(models.Expense).all()
    return templates.TemplateResponse(
        "index.html", {"request": request, "expenses": expenses}
    )


@app.post("/add")
def add_expense(
    title: str = Form(...), amount: float = Form(...), db: Session = Depends(get_db)
):
    expense = models.Expense(title=title, amount=amount)
    db.add(expense)
    db.commit()
    return RedirectResponse("/", status_code=303)


@app.post("/delete/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.query(models.Expense).filter(models.Expense.id == expense_id).first()
    if expense:
        db.delete(expense)
        db.commit()
    return RedirectResponse("/", status_code=303)
