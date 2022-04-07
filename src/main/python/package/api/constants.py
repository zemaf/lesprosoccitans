# import json
import os
from pathlib import Path

from pprint import PrettyPrinter

# pour éviter les pbs de permissions on va stocker les notes dans le dossier utilisateur
# os.path.join(chemin, str) concatène 'chemin' et 'str' pour fabriquer un chemin intelligible sur mac, windows ou linux
MES_PROSPECTS = os.path.join(Path.home(), "MES_PROSPECTS")  # Path.home() = dossier de l'utilisateur courant
# idem avec la liste des artisans que l'utilisateur pourra ainsi mettre à jour depuis sa session
LISTE_PROS_OCCITANS = os.path.join(Path.home(), "LISTE_PROS_OCCITANS")

# Enreistrement de la list des artsians sous LISTE_PROS_OCCITANS

# liste_artisans = pd.read_excel('/Users/imaf/my_python_projects/pro_occitans/src/main/resources/base/liste_Pros_occ.xlsx', 'listing', dtype=object)
# liste_artisans = liste_artisans.set_index('NOM')
# LISTE_ARTISANS = liste_artisans.to_dict('index')
#
# with open(LISTE_PROS_OCCITANS, "w") as f:
#     json.dump(LISTE_ARTISANS, f, ensure_ascii=False, indent=4)




