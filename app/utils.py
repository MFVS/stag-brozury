import os
import pandas as pd
import httpx
from io import StringIO
import time


def get_tituly(titul_pred: str, titul_za: str, jmeno: str) -> str:
    if str(titul_pred) != "nan":
        jmeno = titul_pred + " " + jmeno
    if str(titul_za) != "nan":
        jmeno = jmeno + ", " + titul_za
    return jmeno


async def a_get_df(url: str, vars: dict) -> pd.DataFrame:
    request = httpx.AsyncClient().get(
        url,
        params=vars,
    )
    response = await request
    df = pd.read_csv(StringIO(response.text), sep=";")
    if df.empty:
        return None

    return df

def get_df(url: str, vars: dict) -> pd.DataFrame:
    request = httpx.Client().get(
        url,
        params=vars,
    )
    response = request
    df = pd.read_csv(StringIO(response.text), sep=";")
    if df.empty:
        return None

    return df
