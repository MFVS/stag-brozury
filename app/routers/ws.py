from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from ..utils import a_get_df
from ..models import StudyProgramme

router = APIRouter(prefix="/ws", tags=["WS"])

templates = Jinja2Templates(directory="app/templates")


@router.post("/programy")
async def get_programs(
    request: Request,
    faculty: str = Form(...),
    study_form: str = Form(...),
    programme_type: str = Form(...),
):
    programme = StudyProgramme(
        faculty=faculty, study_form=study_form, programme_type=programme_type
    )
    url = "https://ws.ujep.cz/ws/services/rest2/programy/getStudijniProgramy"
    vars = {
        "fakulta": "PRF",  # programme.faculty,
        "pouzePlatne": True,
        "jazyk": "CZ",
        "lang": "cs",
        "outputFormat": "CSV",
        "outputFormatEncoding": "utf-8",
        # "rok": 2023,
        "typ": programme.programme_type,
        "forma": programme.study_form,
    }

    df = await a_get_df(url, vars)

    if df.empty:
        html_content = """
            <div class="container has-text-centered">
            <div class="notification is-warning">
                Nebyl nalezen žádný studijní program, který by odpovídal paramterům vyhledávání.
            </div>
            </div>
            """
        return HTMLResponse(html_content, status_code=200)
    else:
        return templates.TemplateResponse(
            "components/programy.html", {"request": request, "df": df}
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


@router.get("/predmety/{obor_idno}/{typ}")
async def get_predmety(request: Request, obor_idno: int, typ: str):
    url = "https://ws.ujep.cz/ws/services/rest2/programy/getPlanyOboru"
    vars = {
        "oborIdno": obor_idno,
        "lang": "cs",
        "outputFormat": "CSV",
        "outputFormatEncoding": "utf-8",
    }

    df = await a_get_df(url, vars)
    stplIdno = df["stplIdno"][0]

    url = "https://ws.ujep.cz/ws/services/rest2/programy/getSegmentyPlanu"

    vars = {
        "stplIdno": stplIdno,
        "lang": "cs",
        "outputFormat": "CSV",
        "outputFormatEncoding": "utf-8",
    }

    df = await a_get_df(url, vars)
    # first row
    sespIdno = df["sespIdno"][0]

    url = "https://ws.ujep.cz/ws/services/rest2/programy/getBlokySegmentu"
    vars = {
        "sespIdno": sespIdno,
        "lang": "cs",
        "outputFormat": "CSV",
        "outputFormatEncoding": "utf-8",
    }

    df = await a_get_df(url, vars)
    blokidno = df["blokIdno"][0]

    url = "https://ws.ujep.cz/ws/services/rest2/predmety/getPredmetyByBlokFullInfo"
    vars = {
        "blokIdno": blokidno,
        "lang": "cs",
        "outputFormat": "CSV",
        "outputFormatEncoding": "utf-8",
    }

    df = await a_get_df(url, vars)

    return templates.TemplateResponse(
        "components/predmety.html", {"request": request, "df": df}
    )
