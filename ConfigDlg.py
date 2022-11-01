from os import walk
from PyQt5.QtCore import QPointF, Qt, QPoint, QByteArray, QRectF
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (
    QMessageBox, QGraphicsRectItem,
    QGraphicsScene, QComboBox, QRadioButton, QButtonGroup, QGroupBox, QListWidgetItem,
    QGraphicsView, QApplication, QLabel, QMainWindow, QMenuBar, QMenu, QHBoxLayout, QListView,
    QToolBar, QAction, QGraphicsTextItem, QGraphicsItemGroup, QDialog, QPushButton, QListWidget,
    QLineEdit, QFormLayout, QStatusBar, QTabWidget, QWidget, QVBoxLayout, QDialogButtonBox, QPlainTextEdit
)
from PyQt5.QtGui import QFont, QBrush, QPainter, QPen, QPixmap, QPolygonF, QImage, QIcon, QStandardItem, QColor
from PyQt5.QtPrintSupport import QPrintPreviewDialog, QPrinter, QPrintDialog

import configparser

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
        self.configFilePath = r'stamp_album.cfg'
        self.configParser.read(self.configFilePath)
        self.createDlg()

    def createDlg(self):
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.Dialog)

        # default Copyright
        self.eCopyRight = QLineEdit()
        # default border type
        self.selectedBorderCombo = QComboBox()
        self.selectedBorderCombo.setMaximumWidth(100)
        # default country
        self.selectedCountryCombo = QComboBox()
        self.selectedCountryCombo.setMaximumWidth(100)
        # default text label font

        # default stamp desc font

        # default stamp nbr font

        # ok /cancel button
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)

        flo = QFormLayout()
        flo.addRow(_("Default Copyright:"), self.eCopyRight)
        flo.addRow(_("Border type"), self.selectedBorderCombo)
        flo.addRow(_("Default Country"), self.selectedCountryCombo)

        flo.addRow(bb)

        self.setLayout(flo)