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
from Databases import DB


class EditStampDlg(QDialog):
    def __init__(self, stampObj, parent=None):
        print("init dialog go")
        super(EditStampDlg, self).__init__(parent)
        self.setWindowTitle("Edit stamp")
        self.setWindowModality(Qt.ApplicationModal)
        self.createDlg(stampObj)

    def createDlg(self, stampObj):
        print("create dialog")
        self.setWindowModality(Qt.ApplicationModal)

        self.setWindowFlags(Qt.Dialog)

        self.eTitle = QLineEdit()
        self.eTitle.setText(stampObj['stampDesc_text'])
        self.eNbr = QLineEdit()
        self.eNbr.setText(stampObj['stampNbr_text'])
        self.eValue = QLineEdit()
        self.eValue.setText(stampObj['stampValue_text'])
        l1 = QLabel()
        l1.setPixmap(stampObj['pixmapitem_image'])

        #button = QPushButton("ok")
        # ok /cancel button
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)

        flo = QFormLayout()
        flo.addRow("Title:", self.eTitle)
        flo.addRow("Nbr", self.eNbr)
        flo.addRow("Value", self.eValue)
        flo.addRow(l1)
        flo.addRow(bb)
        #flo.addRow(button)
        self.setLayout(flo)
        #self.retStampObj = stampObj
        #self.eTitle.text()



    # def accept(self):
    #     print("accept")
    #     #self.retStampObj['stampDesc_text'] =
    #     self.close()


