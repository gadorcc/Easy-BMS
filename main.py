from fastapi import FastAPI, Query, Path, HTTPException, status, Body, Request
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from database import iots
from starlette.status import HTTP_400_BAD_REQUEST
from fastapi.responses import HTMLResponse

templates = Jinja2Templates(directory="templates")

class Iot(BaseModel):
    mode: Optional[int] = 0
    name: Optional[str]
    description: Optional[str]
    value: Optional[float]
    type: Optional[str]
    updateAt: Optional[List[str]]

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request, "title": "FastAPI - Home"})

@app.get("/iots", response_model=List[Dict[str, Iot]])
def get_iots(number: Optional[str] = Query("10", max_length=3)):
    response = []
    for id, iot in list(iots.items())[:int(number)]:
        to_add = {}
        to_add[id] = iot
        response.append(to_add)
    return response

@app.get("/iots/{id}", response_model=Iot)
def get_iot_by_id(id: int = Path(...,ge=0,lt=1000)):
    iot = iots.get(id)
    if not iot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Could not find the iot in the database")
    return iot

@app.post("/iots", status_code=status.HTTP_201_CREATED)
def add_iots(body_iots: List[Iot], min_id: Optional[int] = Body(0)):
    if len(body_iots) < 1:
        raise HTTPException(status_code= HTTP_400_BAD_REQUEST, detail="No IoT to add")
    min_id = len(iots.values()) + min_id
    for iot in body_iots:
      while iots.get(min_id):
        min_id += 1
      iots[min_id] = iot
      min_id += 1

@app.put("/iots/{id}",response_model=Dict[str,Iot])
def update_iot(id: int, iot: Iot = Body(...)):
    stored = iots.get(id)
    if not stored:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Could not find IoT given")
    stored = Iot(**stored)
    new = iot.dict(exclude_unset=True)
    new = stored.copy(update=new)
    iots[id] = jsonable_encoder(new)
    response = {}
    response[id] = iots[id]
    return response

@app.delete("/iots/{id}")
def delete_iot(id: int):
  if not iots.get(id):
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Could not find IoT given")

  del iots[id]
