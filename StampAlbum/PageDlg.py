import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QRadioButton, QGroupBox,
    QLabel, QHBoxLayout, QVBoxLayout, QDialogButtonBox, QComboBox, QFormLayout
)
from PyQt6.QtGui import QPixmap
from PageBorder import PageBorder
from StampAlbum.SAAppPaths import get_config_value

import gettext
from StampAlbum.AppLanguage import get_language
gettext.find("PageDlg")
translate = gettext.translation('PageDlg', localedir='locale', languages=[get_language()], fallback=True)
translate.install()
_ = translate.gettext

class PageDlg(QDialog):
    def __init__(self, parent=None):
        super(PageDlg, self).__init__(parent)
        self.setWindowTitle(_("Create new Page"))
        self.pageType = "portrait"

        # Résolution dynamique du dossier d'Images
        self.base_dir = self._get_app_dir()
        self.images_dir = self._get_resource_dir("Images")

        self.borderStyle = self.get_configured_border_style()
        self.createDlg()

    def _get_app_dir(self) -> Path:
        """Détermine le répertoire racine de l'application."""
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).resolve().parent
        else:
            script_dir = Path(__file__).resolve().parent
            parent_dir = script_dir.parent

            if any((parent_dir / folder).exists() for folder in ["Databases", "Images", "photos", "docs","Help", "locale"]):
                return parent_dir

            return script_dir

    def _get_resource_dir(self, folder_name: str) -> Path:
        """Résout le dossier de ressources spécifié."""
        res_dir = self.base_dir / folder_name
        if res_dir.exists():
            return res_dir
        return Path(__file__).resolve().parent / folder_name

    def _get_pixmap(self, image_filename: str) -> QPixmap:
        """Charge une image QPixmap depuis le dossier 'Images' de façon sécurisée."""
        image_path = self.images_dir / image_filename
        if image_path.exists():
            return QPixmap(str(image_path))
        return QPixmap(f"../Images/{image_filename}")

    def get_configured_border_style(self) -> str:
        """Récupère le style de bordure configuré par défaut dans le fichier .cfg."""
        return get_config_value('type encadrement', PageBorder.STYLE_TRIPLE)

    def createDlg(self):
        # page photo
        self.photo = QLabel()
        self.photo.setFixedHeight(200)
        self.photo.setFixedWidth(200)
        self.photo.setPixmap(self._get_pixmap("portrait.png"))

        rbtn1 = QRadioButton(_('Portrait'))
        rbtn2 = QRadioButton(_('Landscape'))

        rbtn1.setChecked(True)

        rbtn1.clicked.connect(self.rbtn1Clicked)
        rbtn2.clicked.connect(self.rbtn2Clicked)

        rbGroup = QGroupBox(_("Select the page:"))
        vbox = QVBoxLayout()
        hBox = QHBoxLayout()
        rbGroup.setLayout(hBox)

        vbox.addWidget(rbtn1)
        vbox.addWidget(rbtn2)

        hBox.addLayout(vbox)
        hBox.addWidget(self.photo)

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
        self.photo.setPixmap(self._get_pixmap("portrait.png"))
        self.pageType = "portrait"

    def rbtn2Clicked(self):
        self.photo.setPixmap(self._get_pixmap("landscape.png"))
        self.pageType = "landscape"

    def onBorderStyleChanged(self, index):
        self.borderStyle = self.borderStyleCombo.currentData()