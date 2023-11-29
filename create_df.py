import pandas as pd
from app.utils import get_df


def create_df():
    url = "https://ws.ujep.cz/ws/services/rest2/programy/getStudijniProgramy"
    vars = {
        "pouzePlatne": True,
        "jazyk": "CZ",
        "lang": "cs",
        "outputFormat": "CSV",
        "outputFormatEncoding": "utf-8",
    }

    df = get_df(url, vars)

    # df.dropna(subset=["garant"], inplace=True)
    # df = df.loc[df["vykazovan"] == "A"]

    url = "https://ws.ujep.cz/ws/services/rest2/programy/getOboryStudijnihoProgramu"

    tmp = [
        get_df(
            url,
            {
                "stprIdno": stprIdno,
                "lang": "cs",
                "outputFormat": "CSV",
                "outputFormatEncoding": "utf-8",
            },
        )
        for stprIdno in df["stprIdno"]
    ]
    df = pd.concat(tmp)

    df.dropna(subset=["anotace"], inplace=True)
    df.dropna(subset=["garant"], inplace=True)

    df.to_csv("df.csv", index=False)


create_df()
