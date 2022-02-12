from email.message import EmailMessage
import getpass
import json
import os
from pprint import PrettyPrinter
from smtplib import SMTP_SSL
import ssl
import vonage

from package.api.constants import MES_PROSPECTS, LISTE_ARTISANS


def decode_tel(numero):
	return numero.replace(numero[0], '33', 1) if numero else None


def get_prospects():
	if not os.path.exists(MES_PROSPECTS):
		with open(MES_PROSPECTS, "w") as f:
			json.dump({}, f, ensure_ascii=False, indent=4)
	else:
		with open(MES_PROSPECTS, "r") as f:
			liste_prospects = json.load(f)  # => {"nom_prospect": {mel: "mel", tel: "tel", ...}}
			# donc k = nom du prospect et d = dictionanire contenant mel, tel, artisan_donneur
			liste_instances = [Prospect(nom=k, **d) for k, d in liste_prospects.items()]
			return liste_instances


def get_prospects_reco():
	liste_instances = get_prospects()
	return (p for p in liste_instances if any([p.artisan_donneur, p.artisan_receveur]))


# je crée un nouveau prospect
class Prospect:
	Mon_Entreprise = 'Ent.Zemaf'

	def __init__(self, nom='', mel='', tel='', adresse='', artisan_donneur='', artisan_receveur=''):
		self.nom = nom.capitalize()
		self.mel = mel
		self.tel = decode_tel(tel) if tel else tel
		self.adresse = adresse
		self.artisan_donneur = artisan_donneur.capitalize()
		self.artisan_receveur = artisan_receveur.capitalize()

	def check_reco(self):
		# vérifie s'il existe un artisan donneur et/ou receveur et retourne un dictionnaire
		liste_cles = ['artisan_donneur', 'artisan_receveur']
		liste_artisan = [self.artisan_donneur, self.artisan_receveur]
		return {cle: nom for cle, nom in zip(liste_cles, liste_artisan) if nom}

	def delete(self):
		with open(MES_PROSPECTS, 'r') as f:
			fichier_prospects = json.load(f)
		del fichier_prospects[self.nom]
		with open(MES_PROSPECTS, 'w') as g:
			json.dump(fichier_prospects, g)

	def envoi_sms(self, artisans, type_evenement='', date=''):  # artisans = check_reco()
		client = vonage.Client(key="c8ad3ef6", secret="buF9VjnvvbcBQXgJ")
		sms = vonage.Sms(client)
		for k in artisans.values():
			tel = LISTE_ARTISANS[k]['tel']
			if "devis" in type_evenement:
				responseData = sms.send_message(
					{
						"from": f"{self.Mon_Entreprise}",
						"to": f"{tel}",
						"text": f"{type_evenement} le {date} entre {self.Mon_Entreprise} et  {self.nom}.\n "
						        f"Je vous informerai de la date de début des travaux",
					}
				)
			else:
				responseData = sms.send_message(
					{
						"from": f"{self.Mon_Entreprise}",
						"to": f"{tel}",
						"text": f"{type_evenement} le {date} entre {self.Mon_Entreprise} et  {self.nom}.\n "
					}
				)

			if responseData["messages"][0]["status"] == "0":
				print("Message sent successfully.")
			else:
				print(f"Message failed with error: {responseData['messages'][0]['error-text']}")

	def envoi_email(self, artisans, type_evenement='', date=''):
		for n in artisans.values():
			email = LISTE_ARTISANS[n]['email']
			smtp_server = 'mail.mailo.com'
			port = 465
			sender_login = 'zemaf@mailo.com'
			password = 'Zwingalouz1973!!'
			# on indique l'alias qu'on veut montrer au receveur
			sender_alias = 'th.begue@testemail.com'
			receiver_email = [email, 'tinoveler@gmail.com']
			message = EmailMessage()
			message["Subject"] = type_evenement
			message["From"] = sender_alias
			# un destinataire
			message["To"] = email
			# on crée un contenu texte
			if "devis" in type_evenement:
				message.set_content(f"{type_evenement} avec {self.nom}"
				                    f"Date: {date}"
				                    f"Vous recevrez un nouvel email pour vous avertir de la date de début des travaux"
				                    f"Cordialement"
				                    f"Ent.Th.Bégué")
				message.add_alternative(f'''
						<html>
							<body>
								<h1>{type_evenement} entre {self.nom} et {self.Mon_Entreprise}!</h1>
								<p>Date: {date}</p>
								<p>Vous recevrez un nouvel email pour vous avertir de la date de début des travaux</p>
								<p>Cordialement.</p>
								<b>Ent.Th.Bégué</b>
							</body>
						</html>
						''', subtype='html')
			else:
				message.set_content(f"{type_evenement} avec {self.nom}"
				                    f"Date: {date}"
				                    f"Merci pour votre recommandation. "
				                    f"Cordialement"
				                    f"Ent.Th.Bégué")
				message.add_alternative(f'''
									<html>
										<body>
											<h1>Bonjour, {type_evenement} entre {self.nom} et {self.Mon_Entreprise}!</h1>
											<p>Date: {date}</p>
											<p>Cordialement.</p>
											<b>Ent.Th.Bégué</b>
										</body>
									</html>
									''',
				                        subtype='html')

			# on crée un contexte ssl sécurisé
			context = ssl.create_default_context()
			# on créé la connexion au serveur avec SMTP_SSL et elle se ferme automatiquement grâce à 'with'
			if email:
				with SMTP_SSL(smtp_server, port, context=context) as server:
					# password = input("Entrez le mot de passe du serveur smtp: ")
					# masque le mot de passe si on est en mode emulateur console dans edit config!!
					# password = getpass.getpass(prompt="Entrez le mot de passe du serveur smtp: ")
					# connexion au compte
					server.login(sender_login, password)
					# envoi du mail
					server.sendmail(sender_alias, receiver_email, message.as_string())
			else:
				print("Vérifier que l'email est bien valide puis recommencez.")

	def save_prospect(self):
		dict_global = {}
		dict_prospect = dict(mel=self.mel, tel=self.tel, adresse=self.adresse)
		dict_prospect.update(self.check_reco())  # on ajoute les clés artisan_donneur/receveur si elles existent

		# on créé dict_global = {nom_prospect : {mel:'...', tel:'...', adresse:'...', artisan_donneur:'...'}}
		dict_global[self.nom] = dict_prospect
		if not os.path.exists(MES_PROSPECTS):
			with open(MES_PROSPECTS, "w") as f:
				json.dump(dict_global, f, ensure_ascii=False, indent=4)
		else:
			with open(MES_PROSPECTS, "r") as g:
				liste_prospects = json.load(g)

			liste_prospects.update(
				dict_global)  # update rajoute les clés du nouveau dictionnaire au dictionnaire initial
			# print(liste_prospects)

			with open(MES_PROSPECTS, "w") as h:
				json.dump(liste_prospects, h, ensure_ascii=False, indent=4)

	def __repr__(self):
		return f"Instance de {self.nom}"


if __name__ == '__main__':
	pp = PrettyPrinter(sort_dicts=True)
	print(decode_tel('0562174000'))

