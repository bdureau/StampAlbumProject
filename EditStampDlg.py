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
        #print(stampObj)
        self.setWindowModality(Qt.ApplicationModal)

        self.setWindowFlags(Qt.Dialog)

        self.eTitle = QPlainTextEdit()
        self.eTitle.setPlainText(stampObj['stampDesc_text'])
        self.eTitle.setFixedHeight(50)

        self.eNbr = QLineEdit()
        self.eNbr.setText(stampObj['stampNbr_text'])

        self.eValue = QPlainTextEdit()
        self.eValue.setPlainText(stampObj['stampValue_text'])
        self.eValue.setFixedHeight(30)
        l1 = QLabel()
        l1.setPixmap(stampObj['pixmapitem_image'])

        # pochettes type
        vLayout1 = QVBoxLayout()
        pochettesType = QLabel("Pochette type")
        self.pochetteList = QListWidget()
        self.pochetteList.setMaximumWidth(150)
        vLayout1.addWidget(pochettesType)
        vLayout1.addWidget(self.pochetteList)


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

        # pochettes type
        vLayout1 = QVBoxLayout()
        pochettesType = QLabel("Pochette type")
        self.pochetteList = QListWidget()
        self.pochetteList.setMaximumWidth(150)
        vLayout1.addWidget(pochettesType)
        vLayout1.addWidget(self.pochetteList)

        #vLayout1.addLayout(flo)
        hLayout2 = QHBoxLayout()
        hLayout2.addLayout(vLayout1)
        hLayout2.addLayout(flo)

        self.setLayout(hLayout2)
        self.populateData(stampObj)



    def populateData(self, stampObj):
        print("")
        self.db = None
        filenames = next(walk("databases"), (None, None, []))[2]  # [] if no file

        # create an array of file name first the open the db with the first one
        self.stampCountries = []
        for file in filenames:
            shortFile = file.rsplit(".")
            if shortFile[0] != "master":
                if shortFile[1] == "mdb":
                    self.stampCountries.append(shortFile[0])

        # open the first country
        if len(self.stampCountries) > 0:
            self.db = DB(self.stampCountries[0])

        # get the list of availble stamp box from the master db
        retBoxList = self.db.loadBoxList()
        self.pochetteList.clear()
        self.pochetteList.addItems(retBoxList)

        retPochette ="Pochette " + str(stampObj['stampBox_boxWidth']) + "x" + str(stampObj['stampBox_boxHeight'])
        if len(retPochette) > 0:
            # print(retPochette[0])
            pochetteItem = self.pochetteList.findItems(retPochette, Qt.MatchExactly)

            if len(pochetteItem) > 0:
                self.pochetteList.setCurrentItem(pochetteItem[0])
            else:
                self.pochetteList.setCurrentRow(0)

    def getBoxInfo(self, box):
        ret = []
        if self.db is not None:
            ret = self.db.getCurrentBox(box)
        return ret