from os import walk
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QRadioButton, QGroupBox,
    QLabel, QHBoxLayout, QVBoxLayout, QDialogButtonBox, QComboBox, QFormLayout
)
from PyQt6.QtGui import QPixmap
from PageBorder import PageBorder
import configparser
from pathlib import Path

import gettext
from AppLanguage import get_language
gettext.find("PageDlg")
translate = gettext.translation('PageDlg', localedir='locale', languages=[get_language()], fallback=True)
translate.install()
_ = translate.gettext

class PageDlg(QDialog):
    def __init__(self, parent=None):
        super(PageDlg, self).__init__(parent)
        self.setWindowTitle(_("Create new Page"))
        self.pageType = "portrait"
        self.borderStyle = self.get_configured_border_style()
        self.createDlg()

    def get_configured_border_style(self) -> str:
        """Récupère le style de bordure configuré par défaut dans le fichier .cfg."""
        config_path = Path(__file__).resolve().parent / 'stamp_album.cfg'
        if config_path.exists():
            parser = configparser.RawConfigParser()
            parser.read(config_path)
            if parser.has_option('CONF', 'type encadrement'):
                return parser.get('CONF', 'type encadrement')
        return PageBorder.STYLE_TRIPLE

    def createDlg(self):
        # page photo
        self.photo = QLabel()
        self.photo.setFixedHeight(200)
        self.photo.setFixedWidth(200)
        self.photo.setPixmap(QPixmap("images/portrait.png"))

        # descChoiceLbl = QLabel("Select the description to use:")
        rbtn1 = QRadioButton(_('Portrait'))
        rbtn2 = QRadioButton(_('Landscape'))

        rbtn1.setChecked(True)

        rbtn1.clicked.connect(self.rbtn1Clicked)
        rbtn2.clicked.connect(self.rbtn2Clicked)

        rbGroup = QGroupBox(_("Select the page:"))
        #vLayout1 = QVBoxLayout()
        vbox = QVBoxLayout()
        hBox = QHBoxLayout()
        rbGroup.setLayout(hBox)

        vbox.addWidget(rbtn1)
        vbox.addWidget(rbtn2)

        hBox.addLayout(vbox)
        hBox.addWidget(self.photo)
        #vLayout1.addWidget(rbGroup)

        # --- Sélection du type de bordure ---
        self.borderStyleCombo = QComboBox()
        self.borderStyleCombo.addItem(_("Triple (Classic)"), PageBorder.STYLE_TRIPLE)
        self.borderStyleCombo.addItem(_("Simple (Frame)"), PageBorder.STYLE_SIMPLE)
        self.borderStyleCombo.addItem(_("Greek (Notched)"), PageBorder.STYLE_GREEK)
        self.borderStyleCombo.addItem(_("Dentelle (Philately)"), PageBorder.STYLE_DENTELLE)

        # Sélectionner par défaut le style configuré
        idx = self.borderStyleCombo.findData(self.borderStyle)
        if idx != -1:
            self.borderStyleCombo.setCurrentIndex(idx)

        self.borderStyleCombo.currentIndexChanged.connect(self.onBorderStyleChanged)

        fLayout = QFormLayout()
        fLayout.addRow(_("Border type:"), self.borderStyleCombo)

        # Layout principal
        vLayout1 = QVBoxLayout()
        vLayout1.addWidget(rbGroup)
        vLayout1.addLayout(fLayout)

        # ok /cancel button
        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                              QDialogButtonBox.StandardButton.Cancel)

        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        vLayout1.addWidget(bb)
        self.setLayout(vLayout1)

    def rbtn1Clicked(self):
        self.photo.setPixmap(QPixmap("images/portrait.png"))
        self.pageType = "portrait"

    def rbtn2Clicked(self):
        self.photo.setPixmap(QPixmap("images/landscape.png"))
        self.pageType = "landscape"

    def onBorderStyleChanged(self, index):
        self.borderStyle = self.borderStyleCombo.currentData()