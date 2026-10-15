import gettext
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QComboBox, QDialogButtonBox, QLabel
from PageBorder import PageBorder
from AppLanguage import get_language

gettext.find("BorderDlg")
translate = gettext.translation('BorderDlg', localedir='locale', languages=[get_language()], fallback=True)
translate.install()
_ = translate.gettext


class BorderDlg(QDialog):
    """Dialogue permettant de choisir un nouveau style de bordure."""

    def __init__(self, current_style=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Choisir un style de bordure"))
        self.resize(300, 100)

        layout = QVBoxLayout(self)

        self.label = QLabel(_("Sélectionnez le nouveau style de bordure :"))
        layout.addWidget(self.label)

        self.combo = QComboBox()
        self.combo.addItem(_("Triple (Classique)"), PageBorder.STYLE_TRIPLE)
        self.combo.addItem(_("Simple (Cadre double)"), PageBorder.STYLE_SIMPLE)
        self.combo.addItem(_("Grec (Coins rentrants)"), PageBorder.STYLE_GREEK)
        self.combo.addItem(_("Dentelle (Philatélie)"), PageBorder.STYLE_DENTELLE)

        # Pré-sélectionne le style actuel de la page
        if current_style:
            index = self.combo.findData(current_style)
            if index != -1:
                self.combo.setCurrentIndex(index)

        layout.addWidget(self.combo)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        layout.addWidget(self.buttonBox)

    def get_style(self):
        """Retourne l'identifiant du style sélectionné."""
        return self.combo.currentData()