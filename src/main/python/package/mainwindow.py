import os
import sys

from functools import partial
import pandas as pd
from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Qt
from PySide6.QtGui import QShortcut, QKeySequence, QStandardItemModel
from PySide6.QtWidgets import QApplication, QAbstractItemView

from package.api.artisan import Prospect, get_pros_occitans, get_prospects, get_prospects_reco

# from package.api.constants import LISTE_ARTISANS


LISTE_LABELS = ["Nom :", "Email :", "Tel: ", "Adresse :"]
LISTE_LABELS_ARTISANS = ["Artisan_donneur", "Artisan_receveur"]


class CustomDialog(QtWidgets.QDialog):
    # On customise une fenêtre Qdialog => INUTILISÉ
    def __init__(self, message='', parent=None):
        super().__init__()
        self.setWindowTitle('ATTENTION!')
        QBtn = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel

        self.buttonBox = QtWidgets.QDialogButtonBox(QBtn)

        self.dialog_layout = QtWidgets.QVBoxLayout()
        texte = QtWidgets.QLabel(message)
        self.dialog_layout.addWidget(texte)
        self.dialog_layout.addWidget(self.buttonBox)

        self.setLayout(self.dialog_layout)


class CustomListItem(QtWidgets.QListWidgetItem):
    pass


class CheckableComboBox(QtWidgets.QComboBox):
    # on crée une combo box avec des éléments que l'on pourra sélectionner et ajouter à l'une ou l'autre des listes
    # artisans donneurs et receveurs
    def __init__(self):
        super().__init__()
        self.liste_artisans = []
        # view() retourne la vue de liste de la combobox
        # view() a un signal "pressed" qui renvoie l'index de l'item sélectionné
        self.view().pressed.connect(self.handle_item_pressed)
        self.setModel(QStandardItemModel(self))

    # when any item get pressed
    def handle_item_pressed(self, index):
        # getting which item is pressed
        item = self.model().itemFromIndex(index)
        # make it check if unchecked and vice-versa
        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
        else:
            item.setCheckState(Qt.Checked)
        # une fois ceci effectué on lance checked_items_list pour peupler les listes donneurs/receveurs
        self.checked_items_list()

    # méthode qui va permettre de peupler la liste des artisans donneurs et receveurs
    def checked_items_list(self):
        # on parcourt la liste des artisans et on ajoute à liste_artisans_donneurs/receveurs les artisans sélectionnés
        for i in range(self.count()):  # self.count() retourne le nb de rangée de 'self' qui est la checkable_cbox
            text_label = self.model().item(i, 0).text()
            # si l'item est coché on l'ajoute à la liste s'il n'y est pas déjà présent
            if self.item_check_status(i) and text_label not in self.liste_artisans:
                self.liste_artisans.append(text_label)
            # quand on désélectionne un artisan qui était présent dans la liste alors on le supprime de la liste
            elif not self.item_check_status(i) and text_label in self.liste_artisans:
                self.liste_artisans.remove(text_label)
        # print(self.liste_artisans)

    # fonction built-in pour empêcher la fermeture de la liste de la combobox à chaque sélection d'artisan
    def hidePopup(self):
        # pas besoin de code pour maintenir la liste affichée pendant la sélection des items!!
        pass

    # method called by checked_items_list
    def item_check_status(self, index):

        # getting item at index
        item = self.model().item(index, 0)

        # return true if checked else false
        return item.checkState() == Qt.Checked


class CustomInputDialog(QtWidgets.QWidget):
    # on prévoit un attribut parent qui correspond au parent de la boite de dialogue créée ici donc la fenêtre
    # principale mainwindow
    def __init__(self, parent=None):
        super().__init__()
        # on crée 2 instances de la classe CheckableComboBox pour peupler les combobox artisans donneurs et receveurs
        donneur_checkable_cbox = CheckableComboBox()
        receveur_checkable_cbox = CheckableComboBox()
        # self.ctx = ctx
        self.parent = parent
        self.ARTISANS = get_pros_occitans()  # on récupère la liste des artisans sous forme de dictionnaire
        self.nom = {'label': "Nom:", 'widget': QtWidgets.QLineEdit()}
        self.mel = {'label': "Email:", 'widget': QtWidgets.QLineEdit()}
        self.tel = {'label': "Tel:", 'widget': QtWidgets.QLineEdit()}
        self.adresse = {'label': "Adresse:", 'widget': QtWidgets.QLineEdit()}
        self.artisan_donneur = {'label': "Artisan donneur:", 'widget': donneur_checkable_cbox}
        # on place l'index à -1 pour pouvoir afficher le placeholder
        self.artisan_donneur['widget'].setCurrentIndex(-1)
        self.artisan_donneur['widget'].setPlaceholderText("Indiquez l'artisan qui a recommandé le prospect:")
        # on peuple la combobox artisans donneurs
        self.artisan_donneur['widget'].addItems(self.ARTISANS.keys())
        self.artisan_receveur = {'label': "Sélectionnez les artisans receveurs:", 'widget': receveur_checkable_cbox}
        self.artisan_receveur['widget'].setCurrentIndex(-1)
        self.artisan_receveur['widget'].setPlaceholderText("Cochez les artisans recommandés")
        # on peuple la checkable_combobox artisans receveurs
        self.artisan_receveur['widget'].addItems(self.ARTISANS.keys())
        self.btn_validate = QtWidgets.QPushButton("OK")
        # on initialise 'dict_prospect' avec les données 'artisan_receveur' récupérées de 'instance_checkable_cbox'
        # => au départ artisan_receveur est vide puis se remplit à chaque clique sur la receveurs_checkable_cbox
        self.dict_prospect = dict(artisan_donneur=donneur_checkable_cbox.liste_artisans,
                                  artisan_receveur=receveur_checkable_cbox.liste_artisans)

        # Layout

        layout = QtWidgets.QFormLayout()
        layout.addRow(self.nom['label'], self.nom['widget'])
        layout.addRow(self.mel['label'], self.mel['widget'])
        layout.addRow(self.tel['label'], self.tel['widget'])
        layout.addRow(self.adresse['label'], self.adresse['widget'])
        layout.addRow(self.artisan_donneur['label'], self.artisan_donneur['widget'])
        layout.addRow(self.artisan_receveur['label'], self.artisan_receveur['widget'])
        layout.addRow("cliquez pour valider", self.btn_validate)
        self.setLayout(layout)
        self.setWindowTitle("Créer un Prospect")

        # Connections

        # editionFinished => signal émis quand on tape enter ou quand on change le focus
        # rmq : quand on tape sur ok on crée self.dict_prospect

        # self.nom['widget'].editingFinished.connect(lambda key="zgeg", lineEdit=self.nom['widget']:
        # self.dict_prospect.update({key: lineEdit.text()}))

        self.nom['widget'].editingFinished.connect(partial(self.populate_dict_prospect,
                                                           "nom", self.nom['widget']))
        self.mel['widget'].editingFinished.connect(partial(self.populate_dict_prospect,
                                                           "mel", self.mel['widget']))
        self.tel['widget'].editingFinished.connect(partial(self.populate_dict_prospect,
                                                           "tel", self.tel['widget']))
        self.adresse['widget'].editingFinished.connect(partial(self.populate_dict_prospect,
                                                               "adresse", self.adresse['widget']))

        # Les listes artisan_donneur/receveur étant peuplées via la fonction checked_items_list
        # de  instance_checkable_cbox on n'a donc pas besoin de la fonction populate_dict_prospect

        self.btn_validate.clicked.connect(self.validate_form)

    def populate_dict_prospect(self, lbl, wdg):
        # on peuple dict_prospect au fur et à mesure que l'on remplit le formulaire 'créer un prospect'
        self.dict_prospect[lbl] = wdg.text()  # ici wdg est un QLineEdit dont on récupère le texte entré

    def validate_form(self):
        # on vérifie la validation du formulaire en s'assurant que le nom du prospect est bien renseigné
        try:
            if self.dict_prospect['nom']:
                prospect = Prospect(**self.dict_prospect)
                prospect.save_prospect()
                self.parent.add_prospect_to_listwidget(prospect)
                self.mel['widget'].clear()
                self.tel['widget'].clear()
                self.adresse['widget'].clear()
                self.close()  # on ferme le formulaire
        except KeyError:
            message_box = QtWidgets.QMessageBox()
            message_box.setWindowTitle("Attention!")  # ne fonctionne pas sur mac os
            message_box.setText("Pas de nom, pas de prospect!")
            message_box.exec()


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # obligatoire d'indiquer le chemin du fichier associé à la mainwindow pour afficher l'icone
        self.setWindowFilePath(os.getcwd())
        self.setWindowTitle('Les_Professionnels_Occitans')
        self.setup_ui()
        if get_prospects():
            self.load_prospect()  # on charge la liste des prospects depuis ~/Mes_Prospects
        self.connect_delete_shortcut()  # on connecte le raccourci clavier "backspace"

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.lbl_liste_prospects = QtWidgets.QLabel('Liste des Prospects')
        self.lbl_detail_prospect = QtWidgets.QLabel('Détails du prospect sélectionné')
        self.lw_afficher_prospects = QtWidgets.QListWidget()
        self.te_details_prospect = QtWidgets.QTextEdit()
        # self.te_details_prospect.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.btn_mes_prospects = QtWidgets.QPushButton('Mes prospects')
        self.btn_delete = QtWidgets.QPushButton('Supprimer prospect')
        self.le_search_prospect = QtWidgets.QLineEdit()
        self.le_search_prospect.setPlaceholderText("Recherche client ")
        # on affiche une croix = "clear button" si le champ recherche n'est pas vide
        self.le_search_prospect.setClearButtonEnabled(True)
        self.btn_prospects_reco = QtWidgets.QPushButton('Mes prospects recommandés')
        self.btn_creer_prospects = QtWidgets.QPushButton('Créer un nouveau prospect')
        self.lbl_instructions = QtWidgets.QLabel('Sélectionnez un prospect avant de cliquer sur les boutons suivants ')
        self.btn_signature_devis = QtWidgets.QPushButton('Signature du devis')
        self.btn_date_fixee = QtWidgets.QPushButton('Date des travaux fixée')

        # test combo box

        # self.btn_test_combo = QtWidgets.QComboBox()
        # self.btn_test_combo.setEditable(True)
        # self.btn_test_combo.setInsertPolicy(QtWidgets.QComboBox.InsertAtCurrent)
        # self.btn_test_combo.addItems(ARTISANS)  # on ajoute une liste d'items

    def modify_widgets(self):
        pass

    def create_layouts(self):
        self.main_layout = QtWidgets.QGridLayout(self)

    def add_widgets_to_layouts(self):
        self.main_layout.addWidget(self.lbl_liste_prospects, 0, 0, 1, 2)
        self.main_layout.addWidget(self.lbl_detail_prospect, 0, 2, 1, 2)
        self.main_layout.addWidget(self.lw_afficher_prospects, 1, 0, 1, 2)
        self.main_layout.addWidget(self.te_details_prospect, 1, 2, 1, 2)
        self.main_layout.addWidget(self.btn_mes_prospects, 2, 0, 1, 2)
        # self.main_layout.addStretch() # ne fonctionne pas avec QGridLayout mais QHBoxLayout
        self.main_layout.addWidget(self.btn_prospects_reco, 2, 2, 1, 2)
        self.main_layout.addWidget(self.le_search_prospect, 3, 0, 1, 1)
        self.main_layout.addWidget(self.btn_delete, 4, 0, 1, 1)
        self.main_layout.addWidget(self.btn_creer_prospects, 5, 1, 1, 2)
        self.main_layout.addWidget(self.lbl_instructions, 6, 1, 1, 2)
        self.main_layout.addWidget(self.btn_signature_devis, 7, 1, 1, 2)
        self.main_layout.addWidget(self.btn_date_fixee, 8, 1, 1, 2)

        # self.main_layout.addWidget(self.btn_test_combo, 8, 1, 1, 2)

    def setup_connections(self):
        self.btn_creer_prospects.clicked.connect(self.creer_prospect)

        self.btn_mes_prospects.clicked.connect(self.load_prospect)

        self.btn_prospects_reco.clicked.connect(self.load_prospects_reco)

        self.btn_delete.clicked.connect(self.delete_prospect)

        self.le_search_prospect.textChanged.connect(self.search_prospect)

        # dès qu'on sélectionne un prospect on affiche son dictionnaire __dict__ via load_prospects
        self.lw_afficher_prospects.itemSelectionChanged.connect(self.display_prospect)

        self.btn_signature_devis.clicked.connect(self.send_notifications)

        self.btn_date_fixee.clicked.connect(self.send_notifications)

        # self.btn_test_combo.textActivated.connect(self.combo_textchanged)

    # END UI

    # on ajoute le nom du nouveau prospect à la liste
    def add_prospect_to_listwidget(self, prospect):
        # prospect est une instance de la classe Prospect

        lw_item = QtWidgets.QListWidgetItem(prospect.nom)  # on créer un QListWidgetItem avec comme texte le nom du
        # prospect
        # lw_item étant un objet, on peut lui créer un attribut 'propsect' qui pointe vers l'instance du prospect
        # Grâce à cela on pourra accéder au prospect et afficher ses attributs, via: instance.__dict__,
        # en cliquant sur lw_item dans le listwidget
        lw_item.prospect = prospect  # lw_item a un attribut prospect qui est une instance de la classe Prospect

        self.lw_afficher_prospects.addItem(lw_item)  # on ajoute l'item au listwidget

    # on connecte le raccourci clavier pour effacer un prospect
    def connect_delete_shortcut(self):
        QShortcut(QKeySequence(QtCore.Qt.Key_Backspace), self, self.delete_prospect)

    # on créé un nouveau prospect, on ajoute son nom à la listwidget et on le sauvegarde dans le fichier MES_PROSPECTS
    def creer_prospect(self):
        # on crée une instance CustomInputDialog
        p = CustomInputDialog(parent=self)
        p.resize(300, 300)
        p.show()

    # def creer_inputDialog(self, titre):
    #     # la méthode getText prend 3 arguments et renvoie un tuple avec le texte entré par l'utilisateur et
    #     # un booléen qui correspond à l'acceptation/rejet du dialogue
    #     att, resultat = QtWidgets.QInputDialog.getText(self, "Créer un prospect", titre)
    #     return att, resultat

    def delete_prospect(self):
        selected_prospect = self.get_selected_lw_item()
        selected_row = self.lw_afficher_prospects.row(selected_prospect)
        if not selected_prospect:
            message_box = QtWidgets.QMessageBox()
            message_box.setWindowTitle("Attention!")  # ne fonctionne pas sur mac os
            message_box.setText("Veuillez sélectionner un prospect dans la liste ci-dessus")
            message_box.exec()
        else:
            selected_prospect.prospect.delete()
            self.lw_afficher_prospects.takeItem(selected_row)
            self.te_details_prospect.clear()

    # on affiche le dictionnaire du prospect sélectionné
    def display_prospect(self):
        # on récupère dans selected_prospect le listwidgetitem sélectionné
        selected_prospect = self.get_selected_lw_item()
        if selected_prospect:
            dict_str = selected_prospect.prospect.__dict__
            # on arrange la présentation du prospect avec 'join'
            pretty_print = "\n\n".join([f"{out.capitalize()}: {dict_str[out]}" for out in dict_str.keys()])
            self.te_details_prospect.setText(pretty_print)

    # on récupère le listwidget item sélectionné
    def get_selected_lw_item(self):
        # 'selectedItems()' retourne une liste de tous les éléments sélectionnés
        selected_items = self.lw_afficher_prospects.selectedItems()
        if selected_items:
            # dans notre appli on ne peut sélectionner qu'un seul élement auquel on accède donc avec l'indice [0]
            return selected_items[0]
        return None

    # on charge les instances de chaque prospect depuis le disque (MES_PROSPECTS)
    def load_prospect(self):
        self.lw_afficher_prospects.clear()
        instances_prospects = get_prospects()  # on récupère la liste des instances de tous les prospects
        for prospect in instances_prospects:  # on ajoute à la listwidget chaque nom de prospect un par un
            self.add_prospect_to_listwidget(prospect)

    def load_prospects_reco(self):
        self.lw_afficher_prospects.clear()
        instances_prospects = get_prospects_reco()  # on récupère la liste des instances de tous les prospects
        for prospect in instances_prospects:  # on ajoute à la listwidget chaque nom de prospect un par un
            self.add_prospect_to_listwidget(prospect)

    def search_prospect(self, txt):
        if not txt:  # si le champ recherche est vide on vide la boite détails prospects
            self.te_details_prospect.clear()
        # on parcourt les rangs un par un
        for i in range(self.lw_afficher_prospects.count()):
            # on récupère le QListWidget item avec son n° de rang
            itm = self.lw_afficher_prospects.item(i)
            # on masque tous les items qui ne contiennent pas la chaine recherchée
            itm.setHidden(txt.lower() not in itm.text().lower())
            # il suffit ensuite de sélectionner l'item pour afficher ses détails

    def send_notifications(self):
        selected_prospect = self.get_selected_lw_item()  # on récupère le prospect sélectionné dans le listwidget
        # on récupère le texte du btn émetteur du signal = 'signature devis' ou 'date des travaux..'
        btn_text = self.sender().text()
        if not selected_prospect:  # message d'erreur si aucun prospect sélectionné au préalable
            message_box = QtWidgets.QMessageBox()
            message_box.setWindowTitle("Attention!")  # ne fonctionne pas sur mac os
            message_box.setText("Veuillez sélectionner un prospect dans la liste ci-dessus")
            message_box.exec()

        else:
            # on va récupérer les infos issus du widget inputdialog grâce à la méthode getText
            # la méthode getText prend 3 arguments et renvoie un tuple avec le texte entré par l'utilisateur et
            # un booléen qui correspond à l'acceptation/rejet du dialogue
            d, resultat = QtWidgets.QInputDialog.getText(self, btn_text, "Date: ?")
            if resultat:  # si le dialogue est validé on envoieles messages
                # prévoir une fonction qui créé un fichier calendrier .ics avec les dates de signature
                # selected_prospect.prospect.creer_evenement_calendrier(date=d,
                #                                             texte_evenement='signature entre artisan et prospect')
                if selected_prospect.prospect.tel:
                    selected_prospect.prospect.envoi_sms(artisans=selected_prospect.prospect.check_reco(),
                                                         type_evenement=btn_text, date=d)
                selected_prospect.prospect.envoi_email(type_evenement=btn_text, date=d,
                                                       artisans=selected_prospect.prospect.check_reco())


if __name__ == '__main__':
    print(__name__)
    # app = QApplication(sys.argv)
    # ex = CustomInputDialog()
    # ex.show()
    # app.exec()
