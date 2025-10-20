from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .config import BASE_DIR
from .database import Base, engine
from .routers import auth, user
from .services.user_services import get_current_user

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Budget Checker")

app.include_router(auth.router)
app.include_router(user.router)

app.mount("/app/static", StaticFiles(directory=BASE_DIR / "app/static"), name="static")


@app.get("/", response_class=HTMLResponse)
def home(request: Request, current_user: Session = Depends(get_current_user)):
    if current_user == 401:
        return RedirectResponse(url="/auth/login", status_code=303)
    return RedirectResponse(url="/user/home", status_code=303)
