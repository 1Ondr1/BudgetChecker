from typing import Union

from fastapi import FastAPI
from models import User

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hellow": "world!"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: User):
    return {"item_name": item.name, "item_id": item_id}
