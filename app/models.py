from pydantic import BaseModel, field_validator
from typing import Any


def normalize_all(value: str) -> Any | None:
    if value == "Vše":
        return None
    return value


class StudyProgramme(BaseModel):
    faculty: str | None
    study_form: str | None  # prezencne atd.
    programme_type: str | None  # bakalar, navazujici atd.

    normalize_all = field_validator("*", mode="before")(normalize_all)

    @field_validator("study_form")
    def check_study_form(cls, v):
        vals_dict = {
            "Prezenční": "P",
            "Kombinovaná": "K",
            "Distanční": "D",
        }

        return vals_dict.get(v)

    @field_validator("programme_type")
    def chech_programme_type(cls, v):
        vals_dict = {"Bakalářský": 7, "Navazující": 0}

        return vals_dict.get(v)
