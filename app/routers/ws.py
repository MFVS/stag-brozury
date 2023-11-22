from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from io import StringIO
from typing import Any
from unidecode import unidecode
import requests
import pandas as pd

from ..utils import a_get_df
from ..models import StudyProgramme, Subject

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
        faculty=faculty,
        study_form=study_form,
        programme_type=programme_type,
        programme=programme,
    )

    df = pd.read_csv("df.csv")

    if study_programme.faculty:
        df = df.loc[df["fakulta"] == study_programme.faculty]
    if study_programme.study_form:
        df = df.loc[df["forma"] == study_programme.study_form]
    if study_programme.programme_type:
        df = df.loc[df["typ"] == study_programme.programme_type]
    if study_programme.programme:
        df = df[
            df["nazev"].apply(unidecode).str.contains(study_programme.programme, case=False, na=False)
        ]

    if df.empty:
        html_content = """
            <div class="container has-text-centered animate__animated animate__fadeIn animate_slower">
            <div class="notification is-light">
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

    df_obor = pd.read_csv(StringIO(requests.get(url, params=vars).text), sep=";")

    obor_idno = df_obor["oborIdno"].iloc[0]

    url = "https://ws.ujep.cz/ws/services/rest2/programy/getPlanyOboru"
    vars = {
        "oborIdno": obor_idno,
        "lang": "cs",
        "outputFormat": "CSV",
        "outputFormatEncoding": "utf-8",
    }

    df = pd.read_csv(StringIO(requests.get(url, params=vars).text), sep=";")

    stplIdno = df["stplIdno"][0]

    url = "https://ws.ujep.cz/ws/services/rest2/programy/getSegmentyPlanu"

    vars = {
        "stplIdno": stplIdno,
        "lang": "cs",
        "outputFormat": "CSV",
        "outputFormatEncoding": "utf-8",
    }

    df_module = pd.read_csv(StringIO(requests.get(url, params=vars).text), sep=";")
    df_module
    temp_dfs = []

    for sesp_idno, nazev_segmentu in zip(
        df_module["sespIdno"], df_module["nazevModulu"]
    ):
        url = "https://ws.ujep.cz/ws/services/rest2/programy/getBlokySegmentu"
        vars = {
            "sespIdno": sesp_idno,
            "lang": "cs",
            "outputFormat": "CSV",
            "outputFormatEncoding": "utf-8",
        }
        temp_df = pd.read_csv(StringIO(requests.get(url, params=vars).text), sep=";")

        for blokidno, nazev_bloku in zip(temp_df["blokIdno"], temp_df["nazev"]):
            url = "https://ws.ujep.cz/ws/services/rest2/predmety/getPredmetyByBlokFullInfo"

            vars = {
                "blokIdno": blokidno,
                "lang": "cs",
                "outputFormat": "CSV",
                "outputFormatEncoding": "utf-8",
            }

            temp_df = pd.read_csv(
                StringIO(requests.get(url, params=vars).text), sep=";"
            )
            temp_df["nazev_segmentu"] = nazev_segmentu
            temp_df["nazev_bloku"] = nazev_bloku
            temp_dfs.append(temp_df)

    df_skupiny = pd.concat(temp_dfs)

    df_skupiny
    # print(df_skupiny.columns)

    df_predmety = df_skupiny[  # "nazev_segmentu",
        ["nazev_bloku", "zkratka", "nazev", "garanti", "kreditu", "vyukaZS", "vyukaLS"]
    ]
    # column semestr ZS if column if vyukaZS == A
    df_predmety["semestr"] = df_predmety["vyukaZS"].apply(
        lambda x: "ZS" if x == "A" else "LS"
    )
    df_predmety["garanti"] = df_predmety["garanti"].str.replace("'", "")
    df_predmety = df_predmety.drop(columns=["vyukaZS", "vyukaLS"])

    df_predmety.columns = ["Blok", "Zkratka", "Název", "Garanti", "Kreditů", "Semestr"]
    df_predmety_str = df_predmety.to_json(orient="records")

    return templates.TemplateResponse(
        "pages/obor.html",
        {
            "request": request,
            "df_obor": df_obor,
            "df_skupiny": df_skupiny,
            "df_predmety": df_predmety,
            "df_predmety_str": df_predmety_str,
        },
    )


@router.post("/predmety")
async def get_predmety_skupiny(
    request: Request,
    idnos: list = Form(alias="stplIdno"),
):
    
    dfs = []

    for idno in idnos:
        url = "https://ws.ujep.cz/ws/services/rest2/programy/getBlokySegmentu"
        vars = {
            "sespIdno": idno,
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
        dfs.append(df)

    df = pd.concat(dfs)
    # print(df.head())

    return templates.TemplateResponse(
        "components/table.html", {"request": request, "df_predmety": df}
    )


@router.post("/filter")
def filter_df(
    request: Request,
    df: str = Form(alias="df"),
    block: str = Form(alias="Blok"),
    shortcut: str = Form(alias="Zkratka"),
    name: str = Form(alias="Název"),
    guarantor: str = Form(alias="Garanti"),
    credits: Any = Form(alias="Kreditů"),
    term: str = Form(alias="Semestr"),
):
    subject = Subject(
        block=block,
        shortcut=shortcut,
        name=name,
        guarantor=guarantor,
        credits=credits,
        term=term,
    )
    
    df_filter = pd.read_json(StringIO(df))

    if subject.block:
        df_filter = df_filter.loc[df_filter["Blok"] == subject.block]
    if subject.shortcut:
        df_filter = df_filter.loc[df_filter["Zkratka"] == subject.shortcut]
    if subject.name:
        df_filter = df_filter.loc[df_filter["Název"] == subject.name]
    if subject.guarantor:
        df_filter = df_filter.loc[df_filter["Garanti"] == subject.guarantor]
    if subject.credits:
        df_filter = df_filter.loc[df_filter["Kreditů"] == subject.credits]
    if subject.term:
        df_filter = df_filter.loc[df_filter["Semestr"] == subject.term]

    return templates.TemplateResponse(
        "components/table.html",
        {
            "request": request,
            "df_predmety": df_filter,
            "df_predmety_str": df,
            "df_predmety_full": pd.read_json(StringIO(df)),
        },
    )
