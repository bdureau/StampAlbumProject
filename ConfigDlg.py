from PageBorder import PageBorder
from os import walk
from pathlib import Path
from PyQt6.QtWidgets import (
    QMessageBox, QGraphicsRectItem,
    QGraphicsScene, QComboBox, QRadioButton, QButtonGroup, QGroupBox, QListWidgetItem,
    QGraphicsView, QApplication, QLabel, QMainWindow, QMenuBar, QMenu, QHBoxLayout, QListView,
    QToolBar, QGraphicsTextItem, QGraphicsItemGroup, QDialog, QPushButton, QListWidget,
    QLineEdit, QFormLayout, QStatusBar, QTabWidget, QWidget, QVBoxLayout, QDialogButtonBox, QPlainTextEdit
)
import configparser
import sys
import gettext

gettext.find("ConfigDlg")
translate = gettext.translation('ConfigDlg', localedir='locale', languages=['fr'])
translate.install()
_ = translate.gettext


class ConfigDlg(QDialog):
    PAPER_A4 = "A4"
    PAPER_LETTER = "Letter"

    def __init__(self, parent=None):
        super(ConfigDlg, self).__init__(parent)
        self.setWindowTitle(_("Application configuration"))
        self.configParser = configparser.RawConfigParser()

        self.base_dir = self.get_app_dir()
        self.configFilePath = self.base_dir / 'stamp_album.cfg'

        self.configParser.read(self.configFilePath)
        self.createDlg()

    def get_app_dir(self) -> Path:
        """Return the base directory path, compatible with PyInstaller frozen executables."""
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).resolve().parent
        else:
            return Path(__file__).resolve().parent

    def createDlg(self):
        # Default Copyright
        self.eCopyRight = QLineEdit()
        self.eCopyRight.setFixedWidth(400)

        # Default Paper Size
        self.selectedPaperCombo = QComboBox()
        self.selectedPaperCombo.setMaximumWidth(200)
        self.selectedPaperCombo.addItem("A4 (210 x 297 mm)", self.PAPER_A4)
        self.selectedPaperCombo.addItem("US Letter (215.9 x 279.4 mm)", self.PAPER_LETTER)

        # Default Border Type
        self.selectedBorderCombo = QComboBox()
        self.selectedBorderCombo.setMaximumWidth(200)
        self.selectedBorderCombo.addItem(_("Triple (Classic)"), PageBorder.STYLE_TRIPLE)
        self.selectedBorderCombo.addItem(_("Simple (Frame)"), PageBorder.STYLE_SIMPLE)
        self.selectedBorderCombo.addItem(_("Greek (Notched)"), PageBorder.STYLE_GREEK)
        self.selectedBorderCombo.addItem(_("Dentelle (Philately)"), PageBorder.STYLE_DENTELLE)

        # Default Country
        self.selectedCountryCombo = QComboBox()
        self.selectedCountryCombo.setMaximumWidth(100)

        # Default Database
        self.selectedDatabaseCombo = QComboBox()
        self.selectedDatabaseCombo.setMaximumWidth(100)

        # OK / Cancel Buttons
        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)

        flo = QFormLayout()
        flo.addRow(_("Default Copyright:"), self.eCopyRight)
        flo.addRow(_("Paper format:"), self.selectedPaperCombo)
        flo.addRow(_("Border type:"), self.selectedBorderCombo)
        flo.addRow(_("Default Country:"), self.selectedCountryCombo)
        flo.addRow(_("Default Database:"), self.selectedDatabaseCombo)
        flo.addRow(bb)

        self.setLayout(flo)
        self.readConfig()

    def readConfig(self):
        filenames = next(walk("databases"), (None, None, []))[2]
        self.stampCountries = []
        for file in filenames:
            shortFile = file.rsplit(".")
            if shortFile[0] != "master" and shortFile[1] == "mdb":
                self.stampCountries.append(shortFile[0])

        self.selectedCountryCombo.addItems(self.stampCountries)
        self.selectedDatabaseCombo.addItem("Access")
        self.selectedDatabaseCombo.addItem("sqlite")

        if self.configParser.has_section('CONF'):
            conf = self.configParser['CONF']
            if self.configParser.has_option('CONF', 'copyright'):
                self.eCopyRight.setText(conf['copyright'])
            if self.configParser.has_option('CONF', 'paper format'):
                paper_fmt = conf['paper format']
                idx = self.selectedPaperCombo.findData(paper_fmt)
                if idx != -1:
                    self.selectedPaperCombo.setCurrentIndex(idx)
            if self.configParser.has_option('CONF', 'default country'):
                self.selectedCountryCombo.setCurrentText(str(conf['default country']))
            if self.configParser.has_option('CONF', 'type encadrement'):
                border_type = conf['type encadrement']
                index = self.selectedBorderCombo.findData(border_type)
                if index != -1:
                    self.selectedBorderCombo.setCurrentIndex(index)
                else:
                    self.selectedBorderCombo.setCurrentText(border_type)
            if self.configParser.has_option('CONF', 'database type'):
                self.selectedDatabaseCombo.setCurrentText(str(conf['database type']))
        else:
            self.configParser["CONF"] = {
                "copyright": "CopyRight © Boris du Reau 2003-2026",
                "paper format": self.PAPER_A4,
                "default country": "France",
                "type encadrement": PageBorder.STYLE_TRIPLE,
                "database type": "sqlite"
            }
            with open(self.configFilePath, 'w') as config:
                self.configParser.write(config)

    def saveConfig(self):
        selected_paper = self.selectedPaperCombo.currentData() or self.PAPER_A4
        selected_border = self.selectedBorderCombo.currentData() or self.selectedBorderCombo.currentText()

        self.configParser["CONF"] = {
            "copyright": self.eCopyRight.text(),
            "paper format": selected_paper,
            "default country": self.selectedCountryCombo.currentText(),
            "type encadrement": selected_border,
            "database type": self.selectedDatabaseCombo.currentText()
        }
        with open(self.configFilePath, 'w') as config:
            self.configParser.write(config)

    def accept(self):
        self.saveConfig()
        self.close()