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
from PyQt6.QtGui import QBrush, QPainter, QPen, QPixmap, QPolygonF, QImage, QIcon, QStandardItem, QColor,QAction
from PyQt6.QtPrintSupport import QPrintPreviewDialog, QPrinter, QPrintDialog
from Databases import DB
from pathlib import Path
from Stamp import Stamp

import gettext
gettext.find("StampDlg")
translate = gettext.translation('StampDlg', localedir='locale', languages=['fr'])
translate.install()
_ = translate.gettext

class StampDlg(QDialog):
    def __init__(self, lastStampObj=None, scene=None, parent=None):
        super(StampDlg, self).__init__(parent)
        self.setWindowTitle(_("Create new stamp"))
        self.currentStampNbr = ""
        self.createDlg(lastStampObj)
        self.scene = scene
        if lastStampObj['country'] is not None:
            print(lastStampObj['country'])
            print(lastStampObj['year'])
            print(lastStampObj['type'])
            print(lastStampObj['nbr'])

    def keyPressEvent(self, e):
        print(e.key())

        if e.key() == Qt.Key.Key_Down:
            #print("down")
            self.stampClicked(self.stampNbrList.currentIndex())
        if e.key() == Qt.Key.Key_Up:
            #print("up")
            self.stampClicked(self.stampNbrList.currentIndex())


    def createDlg(self, lastStampObj):
        #self.setWindowModality(Qt.ApplicationModal)
        #self.setWindowFlags(Qt.Dialog)

        # pochettes type
        vLayout1 = QVBoxLayout()
        pochettesType = QLabel(_("Pochette type"))
        self.pochetteList = QListWidget()
        self.pochetteList.setMaximumWidth(150)
        vLayout1.addWidget(pochettesType)
        vLayout1.addWidget(self.pochetteList)

        # where to go if the pochette is clicked
        self.pochetteList.itemClicked.connect(self.pochetteClicked)

        # Years
        years = QLabel(_("Years:"))
        self.yearsList = QListWidget()
        self.yearsList.setMaximumWidth(100)
        vLayoutYear = QVBoxLayout()

        vLayoutYear.addWidget(years)
        vLayoutYear.addWidget(self.yearsList)

        # where to go if the year is clicked
        self.yearsList.itemClicked.connect(self.yearClicked)
        self.yearsList.itemChanged.connect(self.yearClicked)
        self.yearsList.currentItemChanged.connect(self.yearChanged)


        # stamp nbr
        stampNbr = QLabel(_("Stamp nbr:"))
        self.stampNbrList = QListView()
        self.stampNbrList.setMaximumWidth(100)
        vLayoutStampNbr = QVBoxLayout()

        vLayoutStampNbr.addWidget(stampNbr)
        vLayoutStampNbr.addWidget(self.stampNbrList)

        # where to go if the stamp is clicked
        # self.stampNbrList.itemClicked.connect(self.stampClicked)
        self.stampNbrList.clicked.connect(self.stampClicked)

        # hlayout to group them
        hLayout2 = QHBoxLayout()
        hLayout2.addLayout(vLayoutYear)
        hLayout2.addLayout(vLayoutStampNbr)

        # vlayout to group them
        vLayout2 = QVBoxLayout()
        vLayout2.addLayout(hLayout2)
        # preview stamp photo
        self.photo = QLabel()
        self.photo.setFixedHeight(200)
        self.photo.setFixedWidth(200)
        self.photo.setPixmap(QPixmap(""))
        vLayout2.addWidget(self.photo)

        self.stampTypeCombo = QComboBox()

        self.stampTypeCombo.setMaximumWidth(250)
        self.stampTypeCombo.currentTextChanged.connect(self.stampTypeClicked)


        self.selectedCountryCombo = QComboBox()
        self.selectedCountryCombo.setMaximumWidth(100)

        self.selectedCountryCombo.currentTextChanged.connect(self.countryClicked)

        self.eWidth = QLineEdit()
        self.eWidth.setMaximumWidth(100)
        self.eHeight = QLineEdit()
        self.eHeight.setMaximumWidth(100)
        self.eYear = QLineEdit()
        self.eYear.setMaximumWidth(100)
        self.eValue = QLineEdit()
        self.eValue.setMaximumWidth(150)

        # descChoiceLbl = QLabel("Select the description to use:")
        rbtn1 = QRadioButton(_('Use description 1'))
        rbtn2 = QRadioButton(_('Use description 2'))
        rbtn3 = QRadioButton(_('Use description 1 and 2'))
        rbtn4 = QRadioButton(_('No description'))

        rbtn3.setChecked(True)

        rbGroup = QGroupBox(_("Select the description to use:"))
        vbox = QVBoxLayout()
        rbGroup.setLayout(vbox)

        vbox.addWidget(rbtn1)
        vbox.addWidget(rbtn2)
        vbox.addWidget(rbtn3)
        vbox.addWidget(rbtn4)

        self.eStampDescription = QPlainTextEdit()
        self.eStampDescription.setFixedHeight(50)
        self.eStampDescription2 = QPlainTextEdit()
        self.eStampDescription2.setFixedHeight(50)


        fLayout = QFormLayout()
        fLayout.addRow(_("Stamp type:"), self.stampTypeCombo)
        fLayout.addRow(_("Selected country:"), self.selectedCountryCombo)
        fLayout.addRow(_("Witdh:"), self.eWidth)
        fLayout.addRow(_("Height:"), self.eHeight)
        fLayout.addRow(_("Year:"), self.eYear)
        fLayout.addRow(_("Value:"), self.eValue)

        fLayout.addRow(_("Stamp description:"), self.eStampDescription)
        fLayout.addRow(_("Stamp description2:"), self.eStampDescription2)

        fLayout.addRow("", rbGroup)

        # ok /cancel button
        createButton = QPushButton(self.tr(_("&Create")))
        createButton.setDefault(True)

        createButton2 = QPushButton(self.tr(_("&Create from size")))
        createButton2.setDefault(True)


        okButton = QPushButton(self.tr(_("&Done")))

        buttonBox = QDialogButtonBox(Qt.Orientation.Horizontal)

        buttonBox.addButton(createButton, QDialogButtonBox.ButtonRole.ActionRole)
        buttonBox.addButton(createButton2, QDialogButtonBox.ButtonRole.ActionRole)

        buttonBox.addButton(okButton, QDialogButtonBox.ButtonRole.ActionRole)

        okButton.clicked.connect(self.accept)
        createButton.clicked.connect(self.createStamp)
        createButton2.clicked.connect(self.createStamp2)

        hLayoutAll = QHBoxLayout()
        hLayoutAll.addLayout(vLayout1)
        hLayoutAll.addLayout(vLayout2)
        hLayoutAll.addLayout(fLayout)

        vLayoutAll = QVBoxLayout()
        vLayoutAll.addLayout(hLayoutAll)
        vLayoutAll.addWidget(buttonBox)
        self.setLayout(vLayoutAll)

        self.populateData(lastStampObj)

    def populateData(self,lastStampObj):

        if lastStampObj['country'] is not None:
            self.currentCountry = lastStampObj['country']
        else:
            self.currentCountry = ""

        # get the list of countries from the databases available
        self.retCountryCombo = []
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

        print("test-1")

        for country in self.stampCountries:
            print(country)
            self.retCountryCombo.append(country)
        print("test0")
        # select the first country available
        self.selectedCountryCombo.addItems(self.retCountryCombo)
        print("test")

        if lastStampObj['country'] is not None:
            self.selectedCountryCombo.setCurrentText(lastStampObj['country'])
        else:
            self.selectedCountryCombo.setCurrentIndex(0)

        self.currentCountry = self.selectedCountryCombo.currentText()

        # open the first country
        #self.db = DB(self.currentCountry)

        # get the list of availble stamp box from the master db
        retBoxList = self.db.loadBoxList()
        self.pochetteList.clear()
        self.pochetteList.addItems(retBoxList)

        # get the stamp type from the current country open DB
        retStampType = self.db.loadStampType()
        self.stampTypeCombo.clear()
        self.stampTypeCombo.addItems(retStampType)

        if lastStampObj['type'] is not None:
            self.stampTypeCombo.setCurrentText(lastStampObj['type'])

        # get the available years from the current country open DB
        retYearList = self.db.loadYearList(self.stampTypeCombo.currentText())
        self.yearsList.clear()
        self.yearsList.addItems(retYearList)

        if lastStampObj['year'] is not None:
            yearItem = self.yearsList.findItems(lastStampObj['year'], Qt.MatchFlag.MatchExactly)
            if len(yearItem) > 0:
                self.yearsList.setCurrentItem(yearItem[0])
            else:
                self.yearsList.setCurrentRow(0)

        if len(self.yearsList.selectedItems()) < 1:
            self.yearsList.setCurrentRow(0)

        # self.yearsList.currentItem().setSelected(True)

        # load all available stamp number for the current year
        retStampNbrList = self.db.loadStampList(self.stampTypeCombo.currentText(), self.yearsList.currentItem().text())
        #print(len(retStampNbrList))

        model = QtGui.QStandardItemModel(self.stampNbrList)
        myIndex = 0
        i = 0
        for it in retStampNbrList:

            myitem = QStandardItem(str(it[1]))
            myitem.setData(it[0], 256)
            model.appendRow(myitem)

            if lastStampObj['nbr'] is not None:
                if str(it[1]) == lastStampObj['nbr']:
                    print("found it !!")
                    print(lastStampObj['nbr'])
                    myIndex = i
            i = i + 1
        self.stampNbrList.setModel(model)


            #nbrItem = self.stampNbrList.findItems(lastStampObj['nbr'], Qt.MatchExactly)
            #print(nbrItem)
             #if len(nbrItem) > 0:
             #    self.stampNbrList.setCurrentItem(nbrItem[0])
             #else:
             #    self.stampNbrList.setCurrentRow(0)

        if len(self.stampNbrList.selectedIndexes()) < 1:
            self.stampNbrList.setCurrentIndex(self.stampNbrList.model().index(myIndex, 0))

        print("step2")

        retitem = self.stampNbrList.model().item(myIndex, 0)
        self.currentStampNbr = retitem.text()

        # get pochette for the current stamp
        stampType = self.stampTypeCombo.currentText()
        stampYear = self.yearsList.currentItem().text()
        stampNbr = retitem.text()
        stampKey = retitem.data(256)

        retPochette = self.db.getPochette(stampNbr, stampType, stampYear, stampKey)

        if len(retPochette) > 0:
            pochetteItem = self.pochetteList.findItems(retPochette[0], Qt.MatchFlag.MatchExactly)

            if len(pochetteItem) > 0:
                self.pochetteList.setCurrentItem(pochetteItem[0])
            else:
                self.pochetteList.setCurrentRow(0)
        #else:
        #    self.pochetteList.setCurrentRow(0)
        self.setStampInfo(retitem)

    def yearChanged(self, year):
        if year is not None:
            #print("year text has changed: %s" % year)
            #print(year.text())
            self.yearClicked(year)

    # year has changed, let's retrieve all the stamps for that year
    def yearClicked(self, year):
        # stampYear, stampCountry, stampType
        #print("year has changed")
        #print("New year class %s" % year)
        #print("New year %s" % year.text())
        #print("Reloading years")
        if year.text() != "":
            if self.db is not None:
                #print("Reloading stamplist")
                #self.stampNbrList.model().removeRow(0)
                # load all available stamp number for the current year
                retStampNbrList = self.db.loadStampList(self.stampTypeCombo.currentText(),
                                                        self.yearsList.currentItem().text())

                model = QtGui.QStandardItemModel(self.stampNbrList)
                for it in retStampNbrList:
                    myitem = QStandardItem(str(it[1]))
                    myitem.setData(it[0], 256)
                    model.appendRow(myitem)

                self.stampNbrList.setModel(model)

                if len(self.stampNbrList.selectedIndexes()) < 1:
                    self.stampNbrList.setCurrentIndex(self.stampNbrList.model().index(0, 0))

                retitem = self.stampNbrList.model().item(0, 0)

                self.setStampInfo(retitem)

    # stamp has changed let's change the image and all the stamp properties
    def stampClicked(self, index):
        # stampKey, stampCountry
        #print("stamp has changed")
        #print("New stamp %s" % index.row())
        retitem = self.stampNbrList.model().item(index.row(), 0)
        self.setStampInfo(retitem)
        self.currentStampNbr = retitem.text()

    def setStampInfo(self, retitem):
        if self.db is not None:
            #print("select pochette")
            # get pochette for the current stamp
            stampType = self.stampTypeCombo.currentText()
            stampYear = self.yearsList.currentItem().text()
            stampNbr = retitem.text()
            stampKey = retitem.data(256)

            retPochette = self.db.getPochette(stampNbr, stampType, stampYear, stampKey)

            if len(retPochette) > 0:
                print(retPochette[0])
                pochetteItem = self.pochetteList.findItems(retPochette[0], Qt.MatchFlag.MatchExactly)

                if len(pochetteItem) > 0:
                    self.pochetteList.setCurrentItem(pochetteItem[0])
                else:
                    self.pochetteList.setCurrentRow(0)
            else:
                self.pochetteList.setCurrentRow(0)

            # blank stamp info
            self.eWidth.setText("")
            self.eHeight.setText("")
            self.eYear.setText("")
            self.eValue.setText("")
            self.eStampDescription.setPlainText("")
            self.eStampDescription2.setPlainText("")

            #print("get all stamp info")
            # get all stamp info
            retStampInfo = self.db.stampChanged(stampNbr, stampKey)
            #print("get all stamp info done")
            if len(retStampInfo) > 0:
                # nbr,year,valuecolor, stampDescription,width, height,sub_nbr,stampDescription1
                self.eWidth.setText(retStampInfo[4])
                self.eHeight.setText(retStampInfo[5])
                self.eYear.setText(retStampInfo[1])
                self.eValue.setText(retStampInfo[2])
                self.eStampDescription.setPlainText(retStampInfo[7])
                self.eStampDescription2.setPlainText(retStampInfo[3])

                stampSubNbr = retStampInfo[6]
                print(stampSubNbr)
                photoName = self.getPhotoName(str(stampNbr), str(stampType), stampSubNbr)
                self.fullPhotoPath = "photos\\" + self.currentCountry + "\\" + photoName

                print(self.fullPhotoPath)
                # check if the file exists
                my_file = Path(self.fullPhotoPath)
                if my_file.is_file():
                    # file exists
                    print("File exist")
                else:
                    print("File does not exist")
                    self.fullPhotoPath = "images\\blanc.jpg"

                if self.photo is not None:
                    pix = QPixmap(self.fullPhotoPath)
                    print(pix)
                    if pix.width() > pix.height():
                        self.photo.setPixmap(QPixmap(self.fullPhotoPath).scaledToWidth(200))
                    else:
                        self.photo.setPixmap(QPixmap(self.fullPhotoPath).scaledToHeight(200))

    def countryClicked(self, country):
        # stampCountry
        #print("Country has changed")

        if country != "":
            if self.db is not None:
                self.db.OpenCountryDB(country)
                self.currentCountry = country
                # get the stamp type from the current country open DB
                print("Reloading stamp type")
                self.stampTypeCombo.clear()
                retStampType = self.db.loadStampType()
                print("after Reloading stamp type")
                self.stampTypeCombo.addItems(retStampType)

    def stampTypeClicked(self, stampType):
        # stampType, stampCountry
        #print("Stamp type has changed")
        #print("New stamp type is %s" % stampType)
        # minYear = self.db.getMinYearForType(stampType)
        # self.db.loadStampList(stampType, minYear)
        if stampType != "":
            if self.db is not None:
                # get the available years from the current country open DB
                self.yearsList.clear()
                retYearList = self.db.loadYearList(self.stampTypeCombo.currentText())
                self.yearsList.addItems(retYearList)

                if len(self.yearsList.selectedItems()) < 1:
                    self.yearsList.setCurrentRow(0)
                    #self.yearsList.itemClicked(0)
                    #self.yearsList.setCurrentItem(0)
                    self.yearsList.currentItem().setSelected(True)
                    #self.yearClicked(self.yearsList.currentItem().text())

    def pochetteClicked(self, item):
        # pochette
        print("Current pochette %s" % item.text())

    def getPhotoName(self, stampNumber, stampType, stampSubNbr):
        print("Get photo name")
        nbr = ""
        subNbr = ""

        if stampSubNbr is not None:
            subNbr = "-" + str(stampSubNbr)
        print(subNbr)

        type = str(stampNumber)[0:2]


        # Aérien
        if type == "A ":
            nbr = "T01-030-" + stampNumber[2:len(stampNumber)] + subNbr + ".jpg"
        # Bloc feuillet
        elif type == "BF":
            nbr = "T01-080-" + stampNumber[3:len(stampNumber)] + subNbr + ".jpg"
        # Service
        elif type == "S ":
            nbr = "T01-170-" + stampNumber[2:len(stampNumber)] + subNbr + ".jpg"
        # bloc carnet
        elif type == "BC":
            nbr = "T01-000-BC" + stampNumber[3:len(stampNumber)] + subNbr + ".jpg"
        # bande
        elif type == "B ":
            nbr = "T01-000-B" + stampNumber[2:len(stampNumber)] + subNbr + ".jpg"
        # paire
        elif type == "P ":
            nbr = "T01-000-P" + stampNumber[2:len(stampNumber)] + subNbr + ".jpg"
        # préoblitéré
        elif type == "PR":
            nbr = "T01-420-" + stampNumber[3:len(stampNumber)] + subNbr + ".jpg"
        # franchise militaire
        elif type == "FM":
            nbr = "T01-190-" + stampNumber[3:len(stampNumber)] + subNbr + ".jpg"
        # taxe
        elif type == "TA":
            nbr = "T01-270-" + stampNumber[3:len(stampNumber)] + subNbr + ".jpg"
        # croix rouge
        elif type == "CR":
            nbr = "T01-565-" + stampNumber[3:len(stampNumber)] + subNbr + ".jpg"
        # Guerre
        elif type == "GU":
            nbr = "T01-150-" + stampNumber[3:len(stampNumber)] + subNbr + ".jpg"
        # Alsace Lorraine
        elif type == "AL":
            nbr = "T01-110-" + stampNumber[3:len(stampNumber)] + subNbr + ".jpg"
        # Journaux
        elif type == "JN":
            nbr = "T01-160-" + stampNumber[3:len(stampNumber)] + subNbr + ".jpg"
        # Petit colis
        elif type == "PC":
            nbr = "T01-120-" + stampNumber[3:len(stampNumber)] + subNbr + ".jpg"
        # colis postaux
        elif type == "CP":
            nbr = "T01-130-" + stampNumber[3:len(stampNumber)] + subNbr + ".jpg"
        # Fiscaux postaux
        elif type == "FP":
            nbr = "T01-140-" + stampNumber[3:len(stampNumber)] + subNbr + ".jpg"
        # CFA
        elif type == "CF":
            nbr = "T01-180-CF-" + stampNumber[3:len(stampNumber)] + subNbr + ".jpg"

        # colonies
        elif type == "CO":
            nbr = "T01-200-" + stampNumber[3:len(stampNumber)] + subNbr + ".jpg"
        # télégraphe
        elif type == "TL":
            nbr = "T01-210-" + stampNumber[3:len(stampNumber)] + subNbr + ".jpg"
        # telegraphe militaire
        elif type == "MT":
            nbr = "T01-211-" + stampNumber[3:len(stampNumber)] + subNbr + ".jpg"
        # téléphone
        elif type == "TE":
            nbr = "T01-215-" + stampNumber[3:len(stampNumber)] + subNbr + ".jpg"
        # Greve
        elif type == "GR":
            nbr = "T01-220-" + stampNumber[3:len(stampNumber)] + subNbr + ".jpg"
        # Poste Montenegrine
        elif type == "PM":
            nbr = "T01-230-" + stampNumber[3:len(stampNumber)] + subNbr + ".jpg"
        # fictifs
        elif type == "F ":
            nbr = "T01-240-" + stampNumber[2:len(stampNumber)] + subNbr + ".jpg"
        # fictifs
        elif type == "F-":
            nbr = "T01-000-F" + stampNumber[2:len(stampNumber)] + subNbr + ".jpg"
        # bienfaisance
        elif type == "BI":
            nbr = "T01-250-" + stampNumber[2:len(stampNumber)] + subNbr + ".jpg"
        # mandat
        elif type == "MA":
            nbr = "T01-251-" + stampNumber[2:len(stampNumber)] + subNbr + ".jpg"
        # distributeur
        elif type == "DI":
            nbr = "T01-260-" + stampNumber[2:len(stampNumber)] + subNbr + ".jpg"
        # instruction
        #elif type == "CI":
        #    nbr = "T01-250-" + stampNumber[2:len(stampNumber)] + subNbr + ".jpg"
        else:
            #COURS INSTRUCTION
            if stampType == "COURS INSTRUCTION":
                nbr = "T01-252-" + stampNumber + subNbr + ".jpg"
            #préoblitéré
            elif stampType == "Préoblitéré COURS INSTRUCTION":
                nbr = "T01-253-" + stampNumber + subNbr + ".jpg"
            elif stampType == "RECOUVREMENT COURS INSTRUCTION":
                nbr = "T01-254-" + stampNumber + subNbr + ".jpg"
            elif stampType.strip() == "TAXES COURS INSTRUCTION":
                nbr = "T01-255-" + stampNumber + subNbr + ".jpg"
            #Poste
            else:
                nbr = "T01-000-" + stampNumber + subNbr + ".jpg"

        return nbr

    def getBoxInfo(self, box):
        ret = []
        if self.db is not None:
            ret = self.db.getCurrentBox(box)
        return ret

    def createStamp(self):
        stampDesc = self.eStampDescription.toPlainText()

        stampValue = self.eValue.text()
        pixmap = ""
        if self.fullPhotoPath is not None:
            pixmap = self.fullPhotoPath

        ret = self.getBoxInfo(self.pochetteList.currentItem().text())
        width = ret[0]
        height = ret[1]

        stampNbr = self.currentStampNbr

        stamp = Stamp()
        stamp.createStamp(self.scene, str(stampNbr), str(stampValue), str(stampDesc),
                          float(width), float(height), float(0), float(0), pixmap)

    def createStamp2(self):
        stampDesc = self.eStampDescription.toPlainText()

        stampValue = self.eValue.text()
        pixmap = ""
        if self.fullPhotoPath is not None:
            pixmap = self.fullPhotoPath

        #ret = self.getBoxInfo(self.pochetteList.currentItem().text())
        #self.eWidth.setText("")
        #self.eHeight.setText("")
        width = self.eWidth.text()
        height = self.eHeight.text()

        stampNbr = self.currentStampNbr

        stamp = Stamp()
        stamp.createStamp(self.scene, str(stampNbr), str(stampValue), str(stampDesc),
                          float(width), float(height), float(0), float(0), pixmap)