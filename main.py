from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from database import iots

class Iot(BaseModel):
    mode: int = 0
    name: str
    description: str
    value: float
    type: str
    updateAt: List[str]

app = FastAPI()

@app.get("/")
def root():
    return {"Welcome to": "Hola"}

@app.get("/iots", response_model=List[Dict[str, Iot]])
def get_iots(number: Optional[str] = Query("10", max_length=3)):
    response = []
    for id, iot in list(iots.items())[:int(number)]:
        to_add = {}
        to_add[id] = iot
        response.append(to_add)
    return response
