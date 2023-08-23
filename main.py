from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from stag_data import get_data, classes

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def home(request: Request):
    departments = list(classes.keys())
    return templates.TemplateResponse(
        "home.html", {"request": request, "katedry": departments}
    )


@app.get("/{katedra}")
async def overview(request: Request, katedra: str):
    data = get_data(katedra)
    return templates.TemplateResponse(
        "predmet.html", {"request": request, "data": data, "katedra": katedra}
    )


@app.get("/favicon.ico")
async def icon():
    return FileResponse("static/favicon.ico")
