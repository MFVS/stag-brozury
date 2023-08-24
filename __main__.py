from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from utils import get_data, classes

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def home(request: Request):
    departments = list(classes.keys())
    return templates.TemplateResponse(
        "home.html", {"request": request, "katedry": departments}
    )


@app.get("/{deparment_short}")
async def overview(request: Request, deparment_short: str):
    data, department = get_data(deparment_short)
    return templates.TemplateResponse(
        "predmet.html", {"request": request, "data": data, "department_short": deparment_short, "department": department}
    )

# FIXME: favicon pomoci route
@app.get("/favicon.ico")
async def icon():
    return FileResponse("static/stag_favcon.ico")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
