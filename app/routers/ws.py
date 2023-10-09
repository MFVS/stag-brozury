from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from ..utils import a_get_df

router = APIRouter(prefix="/ws", tags=["WS"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/programy")
async def get_programs(request: Request):
    url = "https://ws.ujep.cz/ws/services/rest2/programy/getStudijniProgramy"
    vars = {
        "fakulta": "PRF",
        "pouzePlatne": True,
        "jazyk": "CZ",
        "lang": "cs",
        "outputFormat": "CSV",
        "outputFormatEncoding": "utf-8",
        "rok": 2023,
        "forma": "P",
    }

    df = await a_get_df(url, vars)

    return templates.TemplateResponse(
        "pages/programy.html", {"request": request, "df": df}
    )


@router.get("/obor/{obor_idno}")
async def get_obor(request: Request, obor_idno: int):
    url = "https://ws.ujep.cz/ws/services/rest2/programy/getOboryStudijnihoProgramu"
    vars = {
        "stprIdno": obor_idno,
        "lang": "cs",
        "outputFormat": "CSV",
        "outputFormatEncoding": "utf-8",
    }

    df = await a_get_df(url, vars)

    return templates.TemplateResponse("pages/obor.html", {"request": request, "df": df})
