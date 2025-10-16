from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import BASE_DIR
from .database import Base, engine
from .routers import auth

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Budget Checker")

app.include_router(auth.router)

app.mount("/app/static", StaticFiles(directory=BASE_DIR / "app/static"), name="static")


@app.get("/")
def home():
    return {"message": "Server is running"}
