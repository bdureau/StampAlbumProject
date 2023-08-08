from os import walk
from PyQt6.QtCore import QPointF, Qt, QPoint, QByteArray, QRectF
from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import (
    QMessageBox,
    QGraphicsRectItem,
    QGraphicsScene, QComboBox, QRadioButton, QButtonGroup, QGroupBox, QListWidgetItem,
    QGraphicsView, QApplication, QLabel, QMainWindow, QMenuBar, QMenu, QHBoxLayout, QListView,
    QToolBar, QGraphicsTextItem, QGraphicsItemGroup, QDialog, QPushButton, QListWidget,
    QLineEdit, QFormLayout, QStatusBar, QTabWidget, QWidget, QVBoxLayout, QDialogButtonBox, QPlainTextEdit
)
from PyQt6.QtGui import QBrush, QPainter, QPen, QPixmap, QPolygonF, QImage, QIcon, QStandardItem, QColor, QAction
from PyQt6.QtPrintSupport import QPrintPreviewDialog, QPrinter, QPrintDialog

import gettext
gettext.find("PageDlg")
translate = gettext.translation('PageDlg', localedir='locale', languages=['fr'])
translate.install()
_ = translate.gettext

class PageDlg(QDialog):
    def __init__(self, parent=None):
        super(PageDlg, self).__init__(parent)
        self.setWindowTitle(_("Create new Page"))
        self.createDlg()

    def createDlg(self):
        self.pageType = "portrait"
        ###########self.setWindowModality(Qt.ApplicationModal)
        #############self.setWindowFlags(Qt.Dialog)

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

        vLayout1 = QVBoxLayout()

        vbox = QVBoxLayout()
        hBox = QHBoxLayout()
        rbGroup.setLayout(hBox)

        vbox.addWidget(rbtn1)
        vbox.addWidget(rbtn2)

        hBox.addLayout(vbox)
        hBox.addWidget(self.photo)
        vLayout1.addWidget(rbGroup)

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