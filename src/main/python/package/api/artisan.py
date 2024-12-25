from email.message import EmailMessage
import getpass
import json
import os
from pprint import PrettyPrinter
from smtplib import SMTP_SSL, SMTP
import ssl
import vonage

from .constants import MES_PROSPECTS, LISTE_PROS_OCCITANS


def decode_tel(numero: str):
	# met le numéro au format "vonage" 33622334455
	return numero.replace(numero[0], '33', 1) if numero else None


def get_pros_occitans():
	# retourne la liste des pros occitans sous forme de dictionnaire
	if not os.path.exists(LISTE_PROS_OCCITANS):
		with open(LISTE_PROS_OCCITANS, "w") as f:
			json.dump({}, f, ensure_ascii=False, indent=4)
	else:
		with open(LISTE_PROS_OCCITANS, "r") as f:
			liste_pros_occitans = json.load(f)  # => {"nom_artisan": {email: "mel", tel: "tel"}, 'nom_artisan2': {}...}
			# donc k = nom du prospect et d = dictionanire contenant mel, tel, artisan_donneur
			return liste_pros_occitans


def get_prospects():
	if not os.path.exists(MES_PROSPECTS):
		with open(MES_PROSPECTS, "w") as f:
			json.dump({}, f, ensure_ascii=False, indent=4)
	else:
		with open(MES_PROSPECTS, "r") as f:
			liste_prospects = json.load(f)  # => {"nom_prospect": {mel: "mel", tel: "tel", ...}}
			# donc k = nom du prospect et d = dictionnaire contenant mel, tel, artisan_donneur
			liste_instances = [Prospect(nom=k, **d) for k, d in liste_prospects.items()]
			return liste_instances


def get_prospects_reco():
	# on récupère une expression génératrice contenant les prospects recommandés pour les afficher dans l'appli
	liste_instances = get_prospects()
	return (p for p in liste_instances if any([p.artisan_donneur, p.artisan_receveur]))


# on détermine tel et mel de l'artisan qui va être contacté, sous forme de dictionnaire de listes
def mel_tel(artisan):
	# artisan est soit un nom d'artisan, soit une liste d'artisans
	liste_mel = []
	liste_tel = []
	LISTE_ARTISANS = get_pros_occitans()
	if isinstance(artisan, str):  # dans le cas d'un artisan_donneur (il n'y en a qu'un)
		mel, tel = LISTE_ARTISANS[artisan]['email'], decode_tel(LISTE_ARTISANS[artisan]['tel'])
		liste_mel.append(mel)
		liste_tel.append(tel)
	elif isinstance(artisan, list):  # on peut avoir de multiples artisans receveurs
		mel, tel = [LISTE_ARTISANS[n]['email'] for n in artisan], [decode_tel(LISTE_ARTISANS[n]['tel']) for n in artisan]
		liste_mel.extend(mel)
		liste_tel.extend(tel)
	return dict(mels=liste_mel, tels=liste_tel)


# je crée un nouveau prospect
class Prospect:
	Mon_Entreprise = 'Ent.XXX'  # signature des mails et sms

	def __init__(self, nom='', mel='', tel='', adresse='', artisan_donneur='', artisan_receveur=None):
		self.nom = nom.capitalize()
		self.mel = mel
		self.tel = decode_tel(tel) if tel else tel
		self.adresse = adresse
		self.artisan_donneur = artisan_donneur
		self.artisan_receveur = [] if artisan_receveur is None else artisan_receveur

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
		for artisan in artisans.values():
			tels = mel_tel(artisan)['tels']  # on récupère la liste des téléphones via mel_tel
			for tel in tels:
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
		# On utilisera soit la connexion sécurisé avec SMTP_SSL, soit la connexion simple -commentée- avec SMTP
		for artisan in artisans.values():
			emails = mel_tel(artisan)['mels']
			for mel in emails:
				smtp_server = 'smtp-relay.sendinblue.com'
				# smtp_server = 'smtp-relay.sendinblue.com' = version sendingblue non sécurisée
				port = 587
				# sender_login = 'zemaf@mailo.com'
				sender_login = 'rb6qqq4c5m@privaterelay.appleid.com'
				# password = 'Zwingalouz1973!!'
				password = 'sYR6dDSBT21I0f4k'
				# on indique l'alias qu'on veut montrer au receveur
				sender_alias = 'pro_occitan@testmail.com'
				receiver_email = [mel]
				print(receiver_email)
				message = EmailMessage()
				message["Subject"] = type_evenement
				message["From"] = sender_alias
				# un destinataire
				message["To"] = mel
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

				# on crée un contexte ssl sécurisé si connexion SMTP_SSL
				# context = ssl.create_default_context()
				# on créé la connexion au serveur avec SMTP_SSL et elle se ferme automatiquement grâce à 'with'
				if mel:
					try:
						with SMTP(smtp_server, port) as server:
						# with SMTP_SSL(smtp_server, port, context=context) as server:
							# password = input("Entrez le mot de passe du serveur smtp: ")
							# masque le mot de passe si on est en mode emulateur console dans edit config!!
							# password = getpass.getpass(prompt="Entrez le mot de passe du serveur smtp: ")
							# connexion au compte
							server.login(sender_login, password)
							# envoi du mail
							server.sendmail(sender_alias, receiver_email, message.as_string())
					except:
						print(f"Pb avec envoi d'email vers {mel}")
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

	print(get_pros_occitans())