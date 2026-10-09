from PageBorder import PageBorder  # Import de la classe de bordures
from os import walk
from PyQt6.QtCore import QPointF, Qt, QPoint, QByteArray, QRectF
from PyQt6 import QtCore, QtGui
from pathlib import Path
from PyQt6.QtWidgets import (
    QMessageBox, QGraphicsRectItem,
    QGraphicsScene, QComboBox, QRadioButton, QButtonGroup, QGroupBox, QListWidgetItem,
    QGraphicsView, QApplication, QLabel, QMainWindow, QMenuBar, QMenu, QHBoxLayout, QListView,
    QToolBar,  QGraphicsTextItem, QGraphicsItemGroup, QDialog, QPushButton, QListWidget,
    QLineEdit, QFormLayout, QStatusBar, QTabWidget, QWidget, QVBoxLayout, QDialogButtonBox, QPlainTextEdit
)
from PyQt6.QtGui import QFont, QBrush, QPainter, QPen, QPixmap, QPolygonF, QImage, QIcon, QAction, QStandardItem, QColor
from PyQt6.QtPrintSupport import QPrintPreviewDialog, QPrinter, QPrintDialog

import configparser
import sys
import gettext
gettext.find("ConfigDlg")
translate = gettext.translation('ConfigDlg', localedir='locale', languages=['fr'])
translate.install()
_ = translate.gettext

class ConfigDlg(QDialog):
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
            # Executable congelé (PyInstaller / CX_Freeze)
            # sys.executable pointe vers le dossier où se trouve le .exe
            return Path(sys.executable).resolve().parent
        else:
            # Script Python normal (.py)
            return Path(__file__).resolve().parent

    def createDlg(self):

        # default Copyright
        self.eCopyRight = QLineEdit()
        self.eCopyRight.setFixedWidth(400)
        # default border type
        self.selectedBorderCombo = QComboBox()
        self.selectedBorderCombo.setMaximumWidth(150)
        self.selectedBorderCombo.addItem("Triple (Classique)", PageBorder.STYLE_TRIPLE)
        self.selectedBorderCombo.addItem("Simple (Filet)", PageBorder.STYLE_SIMPLE)
        self.selectedBorderCombo.addItem("Grecque (Encoches)", PageBorder.STYLE_GREEK)
        self.selectedBorderCombo.addItem("Dentelle (Philatélie)", PageBorder.STYLE_DENTELLE)
        # default country
        self.selectedCountryCombo = QComboBox()
        self.selectedCountryCombo.setMaximumWidth(100)
        # default database
        self.selectedDatabaseCombo = QComboBox()
        self.selectedDatabaseCombo.setMaximumWidth(100)
        # default text label font

        # default stamp desc font

        # default stamp nbr font

        # ok /cancel button
        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)

        flo = QFormLayout()
        flo.addRow(_("Default Copyright:"), self.eCopyRight)
        flo.addRow(_("Border type:"), self.selectedBorderCombo)
        flo.addRow(_("Default Country:"), self.selectedCountryCombo)
        flo.addRow(_("Default Database:"), self.selectedDatabaseCombo)

        flo.addRow(bb)

        self.setLayout(flo)
        self.readConfig()


    # def readConfig_old(self):
    #     print("read")
    #
    #     # get the list of countries from the databases available
    #     self.retCountryCombo = []
    #     filenames = next(walk("databases"), (None, None, []))[2]  # [] if no file
    #
    #     # create an array of file name first the open the db with the first one
    #     self.stampCountries = []
    #     for file in filenames:
    #         shortFile = file.rsplit(".")
    #         if shortFile[0] != "master":
    #             if shortFile[1] == "mdb":
    #                 self.stampCountries.append(shortFile[0])
    #
    #     for country in self.stampCountries:
    #         self.retCountryCombo.append(country)
    #     # select the first country available
    #     self.selectedCountryCombo.addItems(self.retCountryCombo)
    #
    #     self.selectedDatabaseCombo.addItem("Access")
    #     self.selectedDatabaseCombo.addItem("sqlite")
    #
    #     if self.configParser.has_section('CONF'):
    #         conf = self.configParser['CONF']
    #         if self.configParser.has_option('CONF', 'copyright'):
    #             self.eCopyRight.setText(conf['copyright'])
    #         if self.configParser.has_option('CONF', 'default country'):
    #             self.selectedCountryCombo.setCurrentText(str(conf['default country']))
    #         if self.configParser.has_option('CONF', 'type encadrement'):
    #             self.selectedBorderCombo.setCurrentText(str(conf['type encadrement']))
    #         if self.configParser.has_option('CONF', 'database type'):
    #             self.selectedDatabaseCombo.setCurrentText(str(conf['database type']))
    #     else:
    #         self.configParser["CONF"] = {
    #             "copyright": "CopyRight © Boris du Reau 2003-2023",
    #             "default country": "France",
    #             "type encadrement": "type 1",
    #             "database type": "sqlite"
    #         }
    #
    #         # Write the above sections to stamp_album.cfg file
    #         with open(self.configFilePath, 'w') as config:
    #             self.configParser.write(config)

    def readConfig(self):
        # get the list of countries from the databases available
        self.retCountryCombo = []

        filenames = next(walk("databases"), (None, None, []))[2]  # [] if no file

        # create an array of file name first the open the db with the first one
        self.stampCountries = []
        for file in filenames:
            shortFile = file.rsplit(".")
            if shortFile[0] != "master":
                if shortFile[1] == "mdb":
                    self.stampCountries.append(shortFile[0])

        for country in self.stampCountries:
            self.retCountryCombo.append(country)
        # select the first country available
        self.selectedCountryCombo.addItems(self.retCountryCombo)

        #self.selectedBorderCombo.addItem("type 1")

        self.selectedDatabaseCombo.addItem("Access")
        self.selectedDatabaseCombo.addItem("sqlite")


        if self.configParser.has_section('CONF'):
            conf = self.configParser['CONF']
            if self.configParser.has_option('CONF', 'copyright'):
                self.eCopyRight.setText(conf['copyright'])
            if self.configParser.has_option('CONF', 'default country'):
                self.selectedCountryCombo.setCurrentText(str(conf['default country']))
            if self.configParser.has_option('CONF', 'type encadrement'):
                border_type = conf['type encadrement']
                # Sélectionne l'élément par sa valeur d'action (userData ou texte)
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
                "default country": "France",
                "type encadrement": PageBorder.STYLE_TRIPLE,
                "database type": "sqlite"
            }
            with open(self.configFilePath, 'w') as config:
                self.configParser.write(config)

    def saveConfig(self):
        # On sauvegarde le code interne du style de bordure (ex: 'triple', 'greek', etc.)
        selected_border = self.selectedBorderCombo.currentData() or self.selectedBorderCombo.currentText()
        self.configParser["CONF"] = {
            "copyright": self.eCopyRight.text(),
            "default country": self.selectedCountryCombo.currentText(),
            "type encadrement": selected_border,
            "database type": self.selectedDatabaseCombo.currentText()
        }
        # Write the above sections to stamp_album.cfg file
        with open(self.configFilePath, 'w') as config:
            self.configParser.write(config)

    def accept(self):
        self.saveConfig()
        self.close()