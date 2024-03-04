from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from io import StringIO
from typing import Any
from unidecode import unidecode
import requests
import pandas as pd

from ..utils import a_get_df, fetch_all_data
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

    # url = "https://ws.ujep.cz/ws/services/rest2/ciselniky/getCiselnik"

    # vars = {
    #     "domena": "PROGRAM",
    #     "lang": "cs",
    #     "outputFormat": "CSV",
    #     "outputFormatEncoding": "utf-8",
    # }

    # response = requests.get(url, params=vars)
    # df = pd.read_csv(StringIO(response.text), sep=";")

    # df[["nazev", "parametry", "nanik"]] = df["nazev"].str.replace(")","").str.split(" \\(", expand=True)
    # df.drop(columns=["nanik"], inplace=True)
    # df[["fakulta", "kod", "typ", "forma", "jazyk"]] = df["parametry"].str.split(", ", expand=True)

    # ciselnik OBOR
    df = pd.read_csv("df.csv")
    
    if study_programme.faculty:
        df = df.loc[df["fakulta"] == study_programme.faculty]
    if study_programme.study_form:
        df = df.loc[df["forma"] == study_programme.study_form]
    if study_programme.programme_type:
        df = df.loc[df["typ"] == study_programme.programme_type]
    if study_programme.programme:
        df = df[
            df["nazev"]
            .apply(unidecode)
            .str.contains(study_programme.programme, case=False, na=False)
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


@router.get("/obor/{stpr_idno}")
async def get_obor(request: Request, stpr_idno: int):
    url = "https://ws.ujep.cz/ws/services/rest2/programy/getOboryStudijnihoProgramu"
    vars = {
        "stprIdno": stpr_idno,
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
        [
            "nazev_bloku",
            "katedra",
            "zkratka",
            "nazev",
            "garanti",
            "kreditu",
            "vyukaZS",
            "vyukaLS",
            "doporucenyRocnik",
        ]
    ]
    # column semestr ZS if column if vyukaZS == A
    df_predmety["semestr"] = df_predmety["vyukaZS"].apply(
        lambda x: "ZS" if x == "A" else "LS"
    )
    df_predmety["garanti"] = df_predmety["garanti"].str.replace("'", "")
    df_predmety = df_predmety.drop(columns=["vyukaZS", "vyukaLS"])

    df_predmety.columns = [
        "Blok",
        "Katedra",
        "Zkratka",
        "Název",
        "Garanti",
        "Kreditů",
        "Rok",
        "Semestr",
    ]
    df_predmety.fillna("—", inplace=True)
    df_predmety["Rok"] = df_predmety["Rok"].apply(lambda x: int(x) if x != "—" else x)
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


@router.get("/predmet/{predmet_zkr}/{katedra}")
def get_predmet(request: Request, predmet_zkr: str, katedra: str):
    url = "https://ws.ujep.cz/ws/services/rest2/predmety/getPredmetInfo"
    vars = {
        "zkratka": predmet_zkr,
        "katedra": katedra,
        "lang": "cs",
        "outputFormat": "CSV",
        "outputFormatEncoding": "utf-8",
    }

    df = pd.read_csv(StringIO(requests.get(url, params=vars).text), sep=";")
    df.fillna("—", inplace=True)
    # print(df.columns)
    # print(df[["jednotekPrednasek","jednotkaPrednasky"]])
    return templates.TemplateResponse(
        "components/predmet_modal.html", {"request": request, "df": df}
    )


@router.post("/filter")
def filter_df(
    request: Request,
    df: str = Form(alias="df"),
    block: str = Form(alias="Blok"),
    department: str = Form(alias="Katedra"),
    shortcut: str = Form(None, alias="Zkratka"),
    name: str = Form(None, alias="Název"),
    guarantor: str = Form(alias="Garanti"),
    credits: Any = Form(alias="Kreditů"),
    year: Any = Form(alias="Rok"),
    term: str = Form(alias="Semestr"),
):
    subject = Subject(
        block=block,
        department=department,
        shortcut=shortcut,
        name=name,
        guarantor=guarantor,
        credits=credits,
        year=year,
        term=term,
    )

    df_filter = pd.read_json(StringIO(df))

    if subject.block:
        df_filter = df_filter.loc[df_filter["Blok"] == subject.block]
    if subject.department:
        df_filter = df_filter.loc[df_filter["Katedra"] == subject.department]
    if subject.shortcut:
        df_filter = df_filter[
            df_filter["Zkratka"]
            .apply(unidecode)
            .str.contains(subject.shortcut, case=False, na=False)
        ]
    if subject.name:
        df_filter = df_filter[
            df_filter["Název"]
            .apply(unidecode)
            .str.contains(subject.name, case=False, na=False)
        ]
    if subject.guarantor:
        df_filter = df_filter.loc[df_filter["Garanti"] == subject.guarantor]
    if subject.credits:
        df_filter = df_filter.loc[df_filter["Kreditů"] == subject.credits]
    if subject.year:
        if subject.year == 100:
            subject.year = "—"
        df_filter = df_filter.loc[df_filter["Rok"] == subject.year]
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
