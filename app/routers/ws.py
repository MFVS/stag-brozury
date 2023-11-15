from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import pandas as pd

from ..utils import a_get_df
from ..models import StudyProgramme

router = APIRouter(prefix="/ws", tags=["WS"])

templates = Jinja2Templates(directory="app/templates")


@router.post("/programy")
async def get_programs(
    request: Request,
    faculty: str = Form(None),
    study_form: str = Form(None),
    programme_type: str = Form(None),
    programme: str = Form(None),    
):
    study_programme = StudyProgramme(
        faculty=faculty, study_form=study_form, programme_type=programme_type, programme=programme
    )

    df = pd.read_csv("df.csv")

    if study_programme.faculty:
        df = df.loc[df["fakulta"] == faculty]
    if study_programme.study_form:
        df = df.loc[df["forma"] == study_form]
    if study_programme.programme_type:
        df = df.loc[df["typ"] == programme_type]
    if study_programme.programme:
        df = df[df['nazev'].str.contains(study_programme.programme, case=False, na=False)]
    
    print(df.typ)

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

    df_obor = await a_get_df(url, vars)
    
    obor_idno = df_obor["oborIdno"][0]

    url = "https://ws.ujep.cz/ws/services/rest2/programy/getPlanyOboru"
    vars = {
        "oborIdno": obor_idno,
        "lang": "cs",
        "outputFormat": "CSV",
        "outputFormatEncoding": "utf-8",
    }

    help_df = await a_get_df(url, vars)
    stplIdno = help_df["stplIdno"][0]
    url = "https://ws.ujep.cz/ws/services/rest2/programy/getSegmentyPlanu"

    vars = {
        "stplIdno": stplIdno,
        "lang": "cs",
        "outputFormat": "CSV",
        "outputFormatEncoding": "utf-8",
    }

    df_skupiny = await a_get_df(url, vars)

    return templates.TemplateResponse(
        "pages/obor.html",
        {"request": request, "df_obor": df_obor, "df_skupiny": df_skupiny},
    )


@router.get("/predmety/{sesp_idno}")
async def get_predmety_skupiny(request: Request, sesp_idno: int):
    url = "https://ws.ujep.cz/ws/services/rest2/programy/getBlokySegmentu"
    vars = {
        "sespIdno": sesp_idno,
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
