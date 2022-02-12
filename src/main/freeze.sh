# on se place dans ~/venv/bin/et on source le fichier activate => venv actif
source ~/fbs_ps6_venv/bin/activate
# on se replace dans le dossier de l'application
cd ~/pro_occitans/
# on efface le précédent dossier target
fbs clean
# on créé l'exécutable
fbs freeze
# on peut rajouter un installeur => décommenter la ligne ci-dessous
fbs installer