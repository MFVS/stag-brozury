import pandas as pd
import httpx
from io import StringIO

# TODO: Předměty podle oborů.

classes = {
    "KI": ["EAPR1", "EAPR2", "ECIS", "EDAV", "ECGR", "NSQL", "RDBS", "EIS"],
    "KMA": ["E101", "E103", "E104", "E105"],
    "KGEO": ["E101", "E100"],
    "KBI": ["E107", "E106", "E105"],
    "KCH": [],
    "KFY": ["E511"],
}


# TODO: async
def get_data(department: str):
    shorts = classes.get(department)
    dfs = []
    url = "https://ws.ujep.cz/ws/services/rest2/predmety/getPredmetInfo"
    # vars = {
    #     "lang": "en",
    #     "outputFormat": "CSV",
    #     "katedra": department,
    #     "rok": "2022",
    #     "outputFormatEncoding": "utf-8",
    # }
    params = f"lang=en&outputFormat=CSV&rok=2022&outputFormatEncoding=utf-8&katedra={department}"
    for short in shorts:
        # data = httpx.get(url, params={**vars, "zkratka": short})
        dfs.append(
            pd.read_csv(
                # StringIO(data.text),
                f"{url}?{params}&zkratka={short}",
                sep=";",
            )
        )
    return dfs
