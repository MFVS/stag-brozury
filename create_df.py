import pandas as pd
from app.utils import a_get_df


url = "https://ws.ujep.cz/ws/services/rest2/programy/getStudijniProgramy"
vars = {
    "pouzePlatne": True,
    "jazyk": "CZ",
    "lang": "cs",
    "outputFormat": "CSV",
    "outputFormatEncoding": "utf-8",
}

df = a_get_df(url, vars)

df.dropna(subset=["garant"], inplace=True)
df = df.loc[df["vykazovan"] == "A"]

url = "https://ws.ujep.cz/ws/services/rest2/programy/getOboryStudijnihoProgramu"

tmp = [
    await a_get_df(
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

print(df.anotace.iloc[0])
print(df.columns)
