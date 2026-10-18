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
        self.setWindowTitle(_("Choose a border style"))
        self.resize(300, 100)

        layout = QVBoxLayout(self)

        self.label = QLabel(_("Select the New border style :"))
        layout.addWidget(self.label)

        self.combo = QComboBox()
        self.combo.addItem(_("Triple (Classic)"), PageBorder.STYLE_TRIPLE)
        self.combo.addItem(_("Simple (Frame)"), PageBorder.STYLE_SIMPLE)
        self.combo.addItem(_("Greek (Notched)"), PageBorder.STYLE_GREEK)
        self.combo.addItem(_("Dentelle (Philately)"), PageBorder.STYLE_DENTELLE)

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