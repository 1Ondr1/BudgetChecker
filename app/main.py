from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .config import BASE_DIR, templates
from .database import Base, engine
from .routers import auth, user

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Budget Checker")

app.include_router(auth.router)
app.include_router(user.router)

app.mount("/app/static", StaticFiles(directory=BASE_DIR / "app/static"), name="static")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
