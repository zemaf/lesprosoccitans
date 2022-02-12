import os
from pathlib import Path

# pour éviter les pbs de permissions on va stocker les notes dans le dossier utilisateur
# os.path.join(chemin, str) concatène 'chemin' et 'str' pour fabriquer un chemin intelligible sur mac, windows ou linux
MES_PROSPECTS = os.path.join(Path.home(), "MES_PROSPECTS")  # Path.home() = dossier de l'utilisateur courant

LISTE_ARTISANS = {'Th.Bégué': {'email': 'th.begue@free.fr',
                               'tel': '33603528332'
                               },
                  'Kiisol': {'email': 'contact@kiisol.fr',
                            'tel': '33610937009'
                             },
                  'Poweet': {'email': 'tinoveler@gmail.com',
                             'tel': '33650591900'
                             }
                  }
# liste = {'nom': 'Poweet', 'prenom': 'Kiisol'}
# for k in liste.values():
#     print(LISTE_ARTISANS[k]['tel'])