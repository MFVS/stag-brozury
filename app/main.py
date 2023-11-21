from fastapi import FastAPI, Request, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

from .routers import ws
from .utils import a_get_df

app = FastAPI(
    docs_url="/docs",
    redoc_url=None,
    title="STAG API",
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    logging.error(f"{request}: {exc_str}")
    content = {"status_code": 10422, "message": exc_str, "data": None}
    return JSONResponse(
        content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("pages/home.html", {"request": request})


@app.get("/favicon.ico")
async def favicon():
    return RedirectResponse(url="/static/stag_favcon.ico")


app.include_router(ws.router)
