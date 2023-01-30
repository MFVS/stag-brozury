import pandas as pd

# Seznam přemětů pro každou katedru. (předměty pro erasmáky)
# TODO: Tahat ze stagu přeměty podle oborů.

katedry = {
    'KI' : ['EAPR1','EAPR2','ECIS','EDAV', 'ECGR', 'NSQL','RDBS', 'EIS'],
    'KMA': ['E101', 'E103', 'E104', 'E105'],
    'KGEO': [],
    'KBI': [],
    'KCH': [],
    'KFY': ['E511']
}

# Vrací seznam informací pro každý předmět dané katedry.

def get_data(katedra):
    zkratky = katedry.get(katedra)
    dfs = []
    for i in zkratky:
        dfs.append(pd.read_csv(f'https://ws.ujep.cz/ws/services/rest2/predmety/getPredmetInfo?zkratka={i}&lang=en&outputFormat=CSV&katedra={katedra}&rok=2022', 
            sep=';', 
            encoding='cp1250'))
    return dfs

