from os import walk
from PyQt5.QtCore import QPointF, Qt, QPoint, QByteArray, QRectF
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (
    QMessageBox,
    QGraphicsRectItem,
    QGraphicsScene, QComboBox, QRadioButton, QButtonGroup, QGroupBox, QListWidgetItem,
    QGraphicsView, QApplication, QLabel, QMainWindow, QMenuBar, QMenu, QHBoxLayout, QListView,
    QToolBar, QAction, QGraphicsTextItem, QGraphicsItemGroup, QDialog, QPushButton, QListWidget,
    QLineEdit, QFormLayout, QStatusBar, QTabWidget, QWidget, QVBoxLayout, QDialogButtonBox, QPlainTextEdit
)
from PyQt5.QtGui import QBrush, QPainter, QPen, QPixmap, QPolygonF, QImage, QIcon, QStandardItem, QColor
from PyQt5.QtPrintSupport import QPrintPreviewDialog, QPrinter, QPrintDialog

class PageDlg(QDialog):
    def __init__(self, parent=None):
        super(PageDlg, self).__init__(parent)
        self.setWindowTitle("Create new Page")
        self.createDlg()

    def createDlg(self):
        print("create dialog")
        self.pageType = "portrait"
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.Dialog)

        # page photo
        self.photo = QLabel()

        self.photo.setFixedHeight(200)
        self.photo.setFixedWidth(200)
        self.photo.setPixmap(QPixmap("images/portrait.png"))

        # descChoiceLbl = QLabel("Select the description to use:")
        rbtn1 = QRadioButton('Portrait')
        rbtn2 = QRadioButton('Landscape')

        rbtn1.setChecked(True)

        rbtn1.clicked.connect(self.rbtn1Clicked)
        rbtn2.clicked.connect(self.rbtn2Clicked)

        rbGroup = QGroupBox("Select the page:")

        vLayout1 = QVBoxLayout()

        vbox = QVBoxLayout()
        rbGroup.setLayout(vbox)

        vbox.addWidget(rbtn1)
        vbox.addWidget(rbtn2)
        vLayout1.addWidget(rbGroup)
        vLayout1.addWidget(self.photo)
        # ok /cancel button
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        vLayout1.addWidget(bb)
        self.setLayout(vLayout1)

    def rbtn1Clicked(self):
        print("clicked portrait")
        self.photo.setPixmap(QPixmap("images/portrait.png"))
        self.pageType = "portrait"

    def rbtn2Clicked(self):
        print("clicked landscape")
        self.photo.setPixmap(QPixmap("images/landscape.png"))
        self.pageType = "landscape"