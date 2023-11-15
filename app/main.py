from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from .routers import ws
from .utils import a_get_df

app = FastAPI(
    docs_url="/docs",
    redoc_url=None,
    title="STAG API",
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("pages/home.html", {"request": request})


@app.get("/favicon.ico")
async def favicon():
    return RedirectResponse(url="/static/stag_favcon.ico")


app.include_router(ws.router)
