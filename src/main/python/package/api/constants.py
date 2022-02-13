import os
from pathlib import Path
import pandas as pd
from pprint import PrettyPrinter

# pour éviter les pbs de permissions on va stocker les notes dans le dossier utilisateur
# os.path.join(chemin, str) concatène 'chemin' et 'str' pour fabriquer un chemin intelligible sur mac, windows ou linux
MES_PROSPECTS = os.path.join(Path.home(), "MES_PROSPECTS")  # Path.home() = dossier de l'utilisateur courant

liste_artisans = pd.read_excel('/Users/imaf/pro_occitans/src/main/resources/base/liste_Pros_occ.xlsx', 'listing', dtype=object)
liste_artisans = liste_artisans.set_index('NOM')

LISTE_ARTISANS = liste_artisans.to_dict('index')


# pp = PrettyPrinter(sort_dicts=True)
# pp.pprint(LISTE_ARTISANS)
# liste = {'nom': 'Poweet', 'prenom': 'Kiisol'}
# for k in liste.values():
#     print(LISTE_ARTISANS[k]['tel'])
