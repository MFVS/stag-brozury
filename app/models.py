from pydantic import BaseModel, field_validator
from typing import Any
from fastapi import Form
from unidecode import unidecode


def normalize_all(value: str) -> Any | None:
    if value == "Vše":
        return None
    return value


class StudyProgramme(BaseModel):
    faculty: str | None
    study_form: str | None  # prezencne atd.
    programme_type: str | None  # bakalar, navazujici atd.
    programme: str | None  # vyhledavani konkretniho predmetu

    normalize_all = field_validator("*", mode="before")(normalize_all)

    # @field_validator("study_form")
    # def check_study_form(cls, v):
    #     vals_dict = {
    #         "Prezenční": "P",
    #         "Kombinovaná": "K",
    #         "Distanční": "D",
    #     }

    #     return vals_dict.get(v)

    @field_validator("programme")
    def uni(cls, v):
        if v:
            return unidecode(v)


class Subject(BaseModel):
    block: str | None
    department: str | None
    shortcut: str | None
    name: str | None
    guarantor: str | None
    credits: int | None
    year: int | None
    term: str | None

    normalize_all = field_validator("*", mode="before")(normalize_all)

    @field_validator("credits", mode="before")
    def str_none(cls, v):
        try:
            return int(v)
        except:
            return None

    @field_validator("shortcut", "name")
    def uni(cls, v):
        if v:
            return unidecode(v)
        
    @field_validator("year", mode="before")
    def year(cls, v):
        if v == "—":
            return 100
