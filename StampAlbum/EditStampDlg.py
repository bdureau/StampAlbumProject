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
from SAAppPaths import list_countries

import gettext
from AppLanguage import get_language
gettext.find("EditStampDlg")
translate = gettext.translation('EditStampDlg', localedir='locale', languages=[get_language()], fallback=True)
translate.install()
_ = translate.gettext


class EditStampDlg(QDialog):
    def __init__(self, stampObj, parent=None):
        super(EditStampDlg, self).__init__(parent)
        self.setWindowTitle(_("Edit stamp"))
        self.createDlg(stampObj)

    def createDlg(self, stampObj):
        self.eTitle = QPlainTextEdit()
        self.eTitle.setPlainText(stampObj['stampDesc_text'])
        self.eTitle.setFixedHeight(50)

        self.eNbr = QLineEdit()
        self.eNbr.setText(stampObj['stampNbr_text'])

        self.eValue = QPlainTextEdit()
        self.eValue.setPlainText(stampObj['stampValue_text'])
        self.eValue.setFixedHeight(30)

        # image
        self.photo = QLabel()
        self.photo.setFixedHeight(200)
        self.photo.setFixedWidth(200)

        # Image pleine résolution conservée à part : le QLabel n'affiche qu'une vignette
        # de 200 px, la relire avec photo.pixmap() dégradait l'image à chaque édition.
        self.fullPixmap = stampObj.get('pixmapItem_image')
        if not isinstance(self.fullPixmap, QPixmap):
            self.fullPixmap = QPixmap()
        self._showPreview(self.fullPixmap)

        # change image button
        imageButton = QPushButton(self.tr(_("&Change image ...")))
        buttonBox = QDialogButtonBox(Qt.Orientation.Horizontal)

        buttonBox.addButton(imageButton, QDialogButtonBox.ButtonRole.ActionRole)
        imageButton.clicked.connect(self.loadImage)

        # pochettes type

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
        self.db = None
        # Liste des pays selon le moteur configuré (.db ou .mdb)
        self.stampCountries = list_countries()

        # Seule la base master est utile ici (liste des pochettes)
        if self.stampCountries:
            try:
                self.db = DB(self.stampCountries[0])
            except Exception as e:
                QMessageBox.critical(self, _("Database error"), str(e))
                self.db = None

        if self.db is None:
            return

        # get the list of available stamp box from the master db
        retBoxList = self.db.loadBoxList()
        self.pochetteList.clear()
        self.pochetteList.addItems(retBoxList)

        retPochette ="Pochette " + str(stampObj['stampBox_boxWidth']) + "x" + str(stampObj['stampBox_boxHeight'])
        if len(retPochette) > 0:
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

    def _showPreview(self, pix):
        if pix is None or pix.isNull():
            return
        if pix.width() > pix.height():
            self.photo.setPixmap(pix.scaledToWidth(200))
        else:
            self.photo.setPixmap(pix.scaledToHeight(200))

    def getPixmap(self):
        """Image pleine résolution à utiliser pour le timbre."""
        return self.fullPixmap

    def loadImage(self):
        options = QFileDialog.Option.DontUseNativeDialog
        # ne pas nommer la 2e valeur "_" : cela masquerait la fonction de traduction gettext
        fileName, _filter = QFileDialog.getOpenFileName(self, "Select picture", "",
                                                        ("all pictures (*.jpg *.jpeg *.png);;PNG (*.png)"),
                                                        options=options)
        if not fileName:
            return
        pix = QPixmap(fileName)
        if not pix.isNull():
            self.fullPixmap = pix
            self._showPreview(pix)

    def changeFont(self):
        print("change font")