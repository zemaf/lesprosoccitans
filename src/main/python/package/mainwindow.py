import os
import sys

from functools import partial
import pandas as pd
from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Qt
from PySide6.QtGui import QShortcut, QKeySequence, QStandardItemModel
from PySide6.QtWidgets import QApplication, QAbstractItemView

from package.api.artisan import Prospect, get_prospects, get_prospects_reco

# from package.api.constants import LISTE_ARTISANS


LISTE_LABELS = ["Nom :", "Email :", "Tel: ", "Adresse :"]
LISTE_LABELS_ARTISANS = ["Artisan_donneur", "Artisan_receveur"]


class CustomDialog(QtWidgets.QDialog):
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
    def __init__(self):
        super(CheckableComboBox, self).__init__()
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

        # calling method
        self.check_items()

    # method called by check_items
    def item_checked(self, index):

        # getting item at index
        item = self.model().item(index, 0)

        # return true if checked else false
        return item.checkState() == Qt.Checked

    # calling method
    def check_items(self):
        # blank list
        checkedItems = []

        # traversing the items
        for i in range(self.count()):
            text_label = self.model().item(i, 0).text()
            # if item is checked add it to the list
            if self.item_checked(i):
                checkedItems.append(text_label)
        print(checkedItems)


class CustomInputDialog(QtWidgets.QWidget):

    def __init__(self, ctx, parent=None):
        super().__init__()
        self.ctx = ctx
        self.ARTISANS = self.create_ARTISANS()
        self.nom = {'label': "Nom:", 'widget': QtWidgets.QLineEdit()}
        self.mel = {'label': "Email:", 'widget': QtWidgets.QLineEdit()}
        self.tel = {'label': "Tel:", 'widget': QtWidgets.QLineEdit()}
        self.adresse = {'label': "Adresse:", 'widget': QtWidgets.QLineEdit()}
        self.artisan_donneur = {'label': "Artisan_donneur:", 'widget': QtWidgets.QComboBox()}
        self.artisan_donneur['widget'].addItems(self.ARTISANS.keys())
        self.artisan_receveur = {'label': "Sélectinnez les artisans_receveurs:", 'widget': CheckableComboBox()}
        self.artisan_receveur['widget'].addItems(self.ARTISANS.keys())
        # self.lw_artisan_receveur = {'label': "lw_art_receveur:", 'widget': QtWidgets.QListWidget()}
        # self.lw_artisan_receveur['widget'].setSelectionMode(QAbstractItemView.MultiSelection)
        # self.lw_artisan_receveur['widget'].addItems(self.ARTISANS.keys())
        self.btn_validate = QtWidgets.QPushButton("OK")
        self.dict_prospect = {}
        self.parent = parent

        # Layout

        layout = QtWidgets.QFormLayout()
        layout.addRow(self.nom['label'], self.nom['widget'])
        layout.addRow(self.mel['label'], self.mel['widget'])
        layout.addRow(self.tel['label'], self.tel['widget'])
        layout.addRow(self.adresse['label'], self.adresse['widget'])
        layout.addRow(self.artisan_donneur['label'], self.artisan_donneur['widget'])
        layout.addRow(self.artisan_receveur['label'], self.artisan_receveur['widget'])
        # layout.addRow(self.lw_artisan_receveur['label'], self.lw_artisan_receveur['widget'])
        layout.addRow("cliquez pour valider", self.btn_validate)
        self.setLayout(layout)
        self.setWindowTitle("Créer un Prospect")

        # Connections

        # editionFinished => signal émis quand on tape enter ou quand on change le focus
        # rmq : quand on tape sur ok on crée self.dict_prospect

        # self.nom['widget'].editingFinished.connect(lambda key="zgeg", lineEdit=self.nom['widget']:
        # self.dict_prospect.update({key: lineEdit.text()}))

        self.nom['widget'].editingFinished.connect(partial(self.create_key, "nom", self.nom['widget']))
        self.mel['widget'].editingFinished.connect(partial(self.create_key, "mel", self.mel['widget']))
        self.tel['widget'].editingFinished.connect(partial(self.create_key, "tel", self.tel['widget']))
        self.adresse['widget'].editingFinished.connect(partial(self.create_key, "adresse", self.adresse['widget']))
        self.artisan_donneur['widget'].textActivated.connect(partial(self.create_key, "artisan_donneur"))
        self.artisan_receveur['widget'].textActivated.connect(partial(self.create_key, "artisan_receveur"))
        self.btn_validate.clicked.connect(self.validate_form)

    def create_ARTISANS(self):
        liste_artisans = pd.read_excel(self.ctx.get_resource('liste_Pros_occ.xlsx'),
                                       'listing', dtype=object)
        liste_artisans = liste_artisans.set_index('NOM')

        return liste_artisans.to_dict('index')

    def create_key(self, lbl, wdg):
        # ATTENTION : wdg est soit un widget (lineedit), soit le texte retourné par le signal textActivated
        if lbl not in ['artisan_donneur', 'artisan_receveur']:
            self.dict_prospect[lbl] = wdg.text()
            # print(self.dict_prospect)
        else:
            self.dict_prospect[lbl] = wdg

    def validate_form(self):

        try:
            print(self.dict_prospect['nom'])
            if self.dict_prospect['nom']:
                prospect = Prospect(**self.dict_prospect)
                prospect.save_prospect()
                self.parent.add_prospect_to_listwidget(prospect)
                self.mel['widget'].clear()
                self.tel['widget'].clear()
                self.adresse['widget'].clear()
                self.close()
        except KeyError:
            message_box = QtWidgets.QMessageBox()
            message_box.setWindowTitle("Attention!")  # ne fonctionne pas sur mac os
            message_box.setText("Pas de nom, pas de prospect!")
            message_box.exec()


class MainWindow(QtWidgets.QWidget):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

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
        self.main_layout.addWidget(self.btn_delete, 3, 0, 1, 1)
        self.main_layout.addWidget(self.btn_creer_prospects, 4, 1, 1, 2)
        self.main_layout.addWidget(self.lbl_instructions, 5, 1, 1, 2)
        self.main_layout.addWidget(self.btn_signature_devis, 6, 1, 1, 2)
        self.main_layout.addWidget(self.btn_date_fixee, 7, 1, 1, 2)

        # self.main_layout.addWidget(self.btn_test_combo, 8, 1, 1, 2)

    def setup_connections(self):
        self.btn_creer_prospects.clicked.connect(self.creer_prospect)

        self.btn_mes_prospects.clicked.connect(self.load_prospect)

        self.btn_prospects_reco.clicked.connect(self.load_prospects_reco)

        self.btn_delete.clicked.connect(self.delete_prospect)

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
        # on crée des attributs 'reco', 'donneur' et 'receveur' pour un prospect qui est recommandé, reçu et/ou envoyé
        lw_item.reco = True if any([
            lw_item.prospect.artisan_donneur,
            lw_item.prospect.artisan_receveur
        ]
        ) else False
        lw_item.donneur = True if lw_item.prospect.artisan_donneur else False
        lw_item.receveur = True if lw_item.prospect.artisan_receveur else False
        self.lw_afficher_prospects.addItem(lw_item)  # on ajoute l'item au listwidget

    # def combo_textchanged(self, t):
    #     print(self.btn_test_combo.currentText())

    # on connecte le raccourci clavier pour effacer un prospect
    def connect_delete_shortcut(self):
        QShortcut(QKeySequence(QtCore.Qt.Key_Backspace), self, self.delete_prospect)

    # on créé un nouveau prospect, on ajoute son nom à la listwidget et on le sauvegarde dans le fichier MES_PROSPECTS
    def creer_prospect(self):
        p = CustomInputDialog(ctx=self.ctx, parent=self)
        p.resize(150, 150)
        p.show()
        # dict_prospect = {}
        # # on crée la liste des titres de chaque InputDialog
        # liste_titres = ["Nom :", "Email :", "Tel: ", "Adresse :", "Artisan_donneur", "Artisan_receveur"]
        # liste_cles = Prospect().__dict__.keys()
        # liste_titres_cles = list(zip(liste_titres, liste_cles))
        # # titre_nom = QtWidgets.QInputDialog.getItem(self, "créer prospect", "nom", ['ali', 'zgeg'])
        # titre_nom = self.creer_inputDialog("Nom :")
        # # pour le nom, si on clique (cancel) ou (ok sans entrer de nom) on sort de la saisie du prospect
        # if not titre_nom[0] or not titre_nom[1]:
        #     message_box = QtWidgets.QMessageBox()
        #     message_box.setWindowTitle("Attention!")  # ne fonctionne pas sur mac os
        #     message_box.setText("Saisie du nom annulée!")
        #     message_box.exec()
        # elif titre_nom[0]:
        #     dict_prospect["nom"] = titre_nom[0]
        #     # on isole le 1er élément de liste_titres_cles et on itère sur le reste acr on ne veut pas répeter le nom
        #     # first_elem = ("Nom :", "nom"), rest_elem = [("Email: ", "mel"), ("Tel: ", "tel"), ...]
        #     first_elem, *rest_elem = liste_titres_cles
        #     for titre, cle in rest_elem:
        #         # if titre == "Nom :":
        #         #     continue
        #         att, resultat = self.creer_inputDialog(titre)
        #         if resultat and att:
        #             dict_prospect[cle] = att
        #         # elif not resultat:
        #         #     dlg = CustomDialog("on quitte la saisie?", self)
        #         #     dlg.buttonBox.accepted.connect()
        #         #
        #         #     dlg.exec()
        # if dict_prospect:
        #     prospect = Prospect(**dict_prospect)  # on créé un nouveau prospect
        #     self.add_prospect_to_listwidget(prospect)  # on ajoute l'instance prospect au listwidget
        #     prospect.save_prospect()  # on l'enregistre

    def creer_inputDialog(self, titre):
        # la méthode getText prend 3 arguments et renvoie un tuple avec le texte entré par l'utilisateur et
        # un booléen qui correspond à l'acceptation/rejet du dialogue
        att, resultat = QtWidgets.QInputDialog.getText(self, "Créer un prospect", titre)
        return att, resultat

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
            dict_str = str(selected_prospect.prospect.__dict__)
            self.te_details_prospect.setText(dict_str)

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

    def send_notifications(self):
        selected_prospect = self.get_selected_lw_item()  # on récupère le prospect sélectionné dans le listwidget
        btn_text = self.sender().text()  # on récupère le texte du btn émetteur du signal
        if not selected_prospect:
            message_box = QtWidgets.QMessageBox()
            message_box.setWindowTitle("Attention!")  # ne fonctionne pas sur mac os
            message_box.setText("Veuillez sélectionner un prospect dans la liste ci-dessus")
            message_box.exec()
        elif selected_prospect and not selected_prospect.reco:
            message_box = QtWidgets.QMessageBox()
            message_box.setWindowTitle("Attention!")  # ne fonctionne pas sur mac os
            message_box.setText("Ce prospect n'a pas été recommandé!")
            message_box.exec()
        else:
            d, resultat = QtWidgets.QInputDialog.getText(self, btn_text, "Date: ?")
            if resultat and selected_prospect.reco:
                if selected_prospect.prospect.tel:
                    selected_prospect.prospect.envoi_sms(artisans=selected_prospect.prospect.check_reco(),
                                                         type_evenement=btn_text, date=d)
                selected_prospect.prospect.envoi_email(type_evenement=btn_text, date=d,
                                                       artisans=selected_prospect.prospect.check_reco())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CustomInputDialog()
    ex.show()
    app.exec()
