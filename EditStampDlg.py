from os import walk
from PyQt6.QtCore import QPointF, Qt, QPoint, QByteArray, QRectF
from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import (
    QMessageBox,
    QGraphicsRectItem, QFileDialog,
    QGraphicsScene, QComboBox, QRadioButton, QButtonGroup, QGroupBox, QListWidgetItem,
    QGraphicsView, QApplication, QLabel, QMainWindow, QMenuBar, QMenu, QHBoxLayout, QListView,
    QToolBar,  QGraphicsTextItem, QGraphicsItemGroup, QDialog, QPushButton, QListWidget,
    QLineEdit, QFormLayout, QStatusBar, QTabWidget, QWidget, QVBoxLayout, QDialogButtonBox, QPlainTextEdit
)
from PyQt6.QtGui import QBrush, QPainter, QPen, QPixmap, QPolygonF, QImage, QIcon, QStandardItem, QAction,QColor
from PyQt6.QtPrintSupport import QPrintPreviewDialog, QPrinter, QPrintDialog
from Databases import DB

import gettext
gettext.find("EditStampDlg")
translate = gettext.translation('EditStampDlg', localedir='locale', languages=['fr'])
translate.install()
_ = translate.gettext


class EditStampDlg(QDialog):
    def __init__(self, stampObj, parent=None):
        super(EditStampDlg, self).__init__(parent)
        self.setWindowTitle(_("Edit stamp"))
        #self.setWindowModality(Qt.ApplicationModal)
        self.createDlg(stampObj)

    def createDlg(self, stampObj):
        #self.setWindowModality(Qt.ApplicationModal)
        #self.setWindowFlags(Qt.Dialog)
        print("createDlg")
        self.eTitle = QPlainTextEdit()
        self.eTitle.setPlainText(stampObj['stampDesc_text'])
        self.eTitle.setFixedHeight(50)

        self.eNbr = QLineEdit()
        self.eNbr.setText(stampObj['stampNbr_text'])

        self.eValue = QPlainTextEdit()
        self.eValue.setPlainText(stampObj['stampValue_text'])
        self.eValue.setFixedHeight(30)

        # image
        print("image")
        self.photo = QLabel()
        self.photo.setFixedHeight(200)
        self.photo.setFixedWidth(200)

        try:
            pix = QPixmap(stampObj['pixmapItem_image'])
            print(pix)
        except:
            print("error")
            return

        if pix.width() > pix.height():
            self.photo.setPixmap(QPixmap(stampObj['pixmapItem_image']).scaledToWidth(200))
        else:
            self.photo.setPixmap(QPixmap(stampObj['pixmapItem_image']).scaledToHeight(200))

        # change image button
        imageButton = QPushButton(self.tr(_("&Change image ...")))
        buttonBox = QDialogButtonBox(Qt.Orientation.Horizontal)

        buttonBox.addButton(imageButton, QDialogButtonBox.ButtonRole.ActionRole)
        imageButton.clicked.connect(self.loadImage)

        # pochettes type
        print("Pochette type")
        vLayout1 = QVBoxLayout()
        pochettesType = QLabel(_("Pochette type"))
        self.pochetteList = QListWidget()
        self.pochetteList.setMaximumWidth(150)
        vLayout1.addWidget(pochettesType)
        vLayout1.addWidget(self.pochetteList)

        # ok /cancel button
        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)

        flo = QFormLayout()
        flo.addRow(_("Title:"), self.eTitle)
        flo.addRow(_("Nbr"), self.eNbr)
        flo.addRow(_("Value"), self.eValue)
        flo.addRow(self.photo)
        flo.addRow(buttonBox)
        flo.addRow(bb)

        # pochettes type
        vLayout1 = QVBoxLayout()
        pochettesType = QLabel(_("Pochette type"))
        self.pochetteList = QListWidget()
        self.pochetteList.setMaximumWidth(150)
        vLayout1.addWidget(pochettesType)
        vLayout1.addWidget(self.pochetteList)

        hLayout2 = QHBoxLayout()
        hLayout2.addLayout(vLayout1)
        hLayout2.addLayout(flo)

        self.setLayout(hLayout2)
        self.populateData(stampObj)

    def populateData(self, stampObj):
        print("populateData")
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

        # get the list of available stamp box from the master db
        retBoxList = self.db.loadBoxList()
        self.pochetteList.clear()
        self.pochetteList.addItems(retBoxList)

        retPochette ="Pochette " + str(stampObj['stampBox_boxWidth']) + "x" + str(stampObj['stampBox_boxHeight'])
        if len(retPochette) > 0:
            # print(retPochette[0])
            pochetteItem = self.pochetteList.findItems(retPochette, Qt.MatchFlag.MatchExactly)

            if len(pochetteItem) > 0:
                self.pochetteList.setCurrentItem(pochetteItem[0])
            else:
                self.pochetteList.setCurrentRow(0)

    def getBoxInfo(self, box):
        ret = []
        if self.db is not None:
            ret = self.db.getCurrentBox(box)
        return ret

    def loadImage(self):
        options = QFileDialog.Option.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Select picture", "",
                                                  ("all pictures (*.jpg *.jpeg *.png);;PNG (*.png)"),
                                                  options=options)
        if self.photo is not None:
            pix = QPixmap(fileName)
            print(pix)
            if pix.width() > pix.height():
                self.photo.setPixmap(QPixmap(fileName).scaledToWidth(200))
            else:
                self.photo.setPixmap(QPixmap(fileName).scaledToHeight(200))

    def changeFont(self):
        print("change font")