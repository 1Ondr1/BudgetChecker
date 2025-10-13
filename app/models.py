from pydantic import BaseModel

class User(BaseModel):
    name: str
    last_name: str
    age: int