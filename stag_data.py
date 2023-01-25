import pandas as pd

katedry = {
    'KI' : ['EAPR1','EAPR2','ECIS','EDAV', 'ECGR', 'RDBS',],
    'KMA': ['E101', 'E103', 'E104', 'E105'],
    'KGEO': [],
    'KBI': [],
    'KCH': [],
    'KFY': ['E511']
}


def get_data(katedra):
    zkratky = katedry.get(katedra)
    dfs = []
    for i in zkratky:
        dfs.append(pd.read_csv(f'https://ws.ujep.cz/ws/services/rest2/predmety/getPredmetInfo?zkratka={i}&lang=en&outputFormat=CSV&katedra={katedra}&rok=2022', 
            sep=';', 
            encoding='cp1250'))
    return dfs

# data = get_data('KI')
# # for i in range(len(data)):
# #     print(data[i]['zkratka'][0])
    
# print(data[0]['prehledLatky'][0])
