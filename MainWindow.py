from PyQt5.QtCore import QPointF, Qt, QPoint, QByteArray, QRectF
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import (
    QMessageBox, QGraphicsPixmapItem,
    QGraphicsRectItem,
    QGraphicsScene, QFileDialog,
    QGraphicsView, QApplication, QLabel, QMainWindow, QMenuBar, QMenu,
    QToolBar, QAction, QGraphicsTextItem, QGraphicsItemGroup, QDialog, QPushButton,
    QLineEdit, QFormLayout, QStatusBar, QTabWidget, QWidget, QVBoxLayout, QDialogButtonBox, QPlainTextEdit
)
from PyQt5.QtGui import QBrush, QPainter, QPen, QPixmap, QPolygonF, QImage, QIcon, QColor, QFont
from PyQt5.QtPrintSupport import QPrintPreviewDialog, QPrinter, QPrintDialog
from Stamp import Stamp

from Page import Page
from ConfigDlg import ConfigDlg
from Databases import DB
import sys
import xml.etree.ElementTree as ET
from StampDlg import StampDlg
from PageDlg import PageDlg
from HelpDlg import HelpDlg
from GraphicsView import GraphicsView
import os, time, gzip
from TextDlg import TextDlg

import gettext


# localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
# print(localedir)
# translate = gettext.translation('MainWindow', localedir, fallback=True)
#_ = translate.gettext
gettext.find("MainWindow")
translate = gettext.translation('MainWindow', localedir='locale', languages=['fr'])
#translate = gettext.translation('MainWindow', localedir='locale', fallback=True)
translate.install()
_ = translate.gettext

class Window(QMainWindow):
    """Main Window."""

    def __init__(self, parent=None):
        """Initializer."""
        super().__init__(parent)
        self.setWindowTitle("Stamp album")
        self.setWindowIcon(QtGui.QIcon('stamp_book1170.png'))
        #self.setMaximumWidth(222 / (25.4 / 96))
        #self.setMaximumWidth(422 / (25.4 / 96))
        self.resize(222 / (25.4 / 96), 800)
        #self.resize(422 / (25.4 / 96), 800)
        self.pageCount = 0
        self.lastStampObj = {}
        self.lastStampObj['country'] = None
        self.lastStampObj['type'] = None
        self.lastStampObj['nbr'] = None
        self.lastStampObj['year'] = None

        # start with no grid
        self.gridOn = False

        self.tabs = QTabWidget()
        palette = self.tabs.palette()
        palette.setColor(self.tabs.backgroundRole(), Qt.lightGray)
        self.tabs.setPalette(palette)
        self.tabs.resize(300, 200)
        self.newPage(None, True)
        self.setCentralWidget(self.tabs)

        self._createActions()
        self._createMenuBar()
        self._createToolBars()
        self._connectActions()

    def closeEvent(self, event):
        print("User has clicked the red x on the main window")
        qm = QMessageBox()
        ret = qm.question(self, 'Exit', "Are you sure you want to exit the application?", qm.Yes | qm.No)

        if ret == qm.Yes:
            event.accept()
        else:
            event.ignore()


    # Create a new page in a tab
    def newPage(self, _pageType=None, border=None):
        if _pageType is not None and (_pageType == 'portrait' or _pageType == 'landscape'):
            self.pageType = _pageType
        else:
            self.pageType = "portrait"
            pDlg = PageDlg()

            res = pDlg.exec_()
            if res == QDialog.Accepted:
                if pDlg.pageType == "portrait":
                    print("portrait")
                    self.pageType = "portrait"
                    border = True
                else:
                    print("landscape")
                    self.pageType = "landscape"
                    border = True

                page = Page(self.pageType, border)

                view = GraphicsView(page)

                view.resize(210 / (25.4 / 96), 297 / (25.4 / 96))
                view.setRenderHint(QPainter.Antialiasing)

                if self.pageType == "portrait":
                    view.setMaximumWidth(210 / (25.4 / 96))
                    view.setMaximumHeight(297 / (25.4 / 96))
                else:
                    view.setMaximumWidth(297 / (25.4 / 96))
                    view.setMaximumHeight(210 / (25.4 / 96))
                #scroll to top
                view.scrollContentsBy(0, 0)
                tab1 = QWidget()
                tab1.layout = QVBoxLayout(self)
                tab1.layout.addWidget(view)
                tab1.setLayout(tab1.layout)
                tab1.setAutoFillBackground(True)

                palette = tab1.palette()
                palette.setColor(tab1.backgroundRole(), Qt.lightGray)
                tab1.setPalette(palette)
                self.pageCount = self.pageCount + 1
                #currentPage = self.tabs.addTab(tab1, "Page " + str(self.pageCount))
                currentPage = self.tabs.insertTab(self.tabs.currentIndex()+1, tab1, "Page " + str(self.tabs.count().real))

                # rename all pages after insert
                #for tab in self.tabs:
                #    self.tabs.currentWidget().setWindowTitle("toto")

                for x in range(0, self.tabs.count().real):
                    self.tabs.setCurrentIndex(x)
                    self.tabs.setTabText(self.tabs.currentIndex(), "Page " + str(x+1))

                self.tabs.setCurrentIndex(currentPage)
                return page

    # delete current page
    def deleteCurrentPage(self):
        qm = QMessageBox()
        ret = qm.question(self, '', "Are you sure you want to delete the current page?", qm.Yes | qm.No)

        if ret == qm.No:
            return
        # only allow delete if number of page is greater than one
        if self.tabs.count().real > 0:
            self.tabs.removeTab(self.tabs.currentIndex())

            for x in range(0, self.tabs.count().real):
                self.tabs.setCurrentIndex(x)
                self.tabs.setTabText(self.tabs.currentIndex(), "Page " + str(x + 1))

    # remove all pages
    def deleteAllPages(self):
        print("Delete all pages")
        for x in range(self.tabs.count()):
            self.tabs.removeTab(self.tabs.currentIndex())
        self.pageCount = 0

    def deleteAlbum(self):
        print("delete current album")
        qm = QMessageBox()
        ret = qm.question(self, 'Delete album', "Are you sure you want to delete the entire album?", qm.Yes | qm.No)

        if ret == qm.No:
            return
        self.deleteAllPages()

    def newBorder(self):
        print("change border")
        print(self.getCurrentPageScene().pageType)
        if self.getCurrentPageScene().pageType == "portrait":
            #self.setSceneRect(0, 0, 210 / (25.4 / 96), 297 / (25.4 / 96))
            self.getCurrentPageScene().addBorder(177 / (25.4 / 96.0),
                           272 / (25.4 / 96.0),
                           19 / (25.4 / 96.0),
                           0,
                           #10 / (25.4 / 96.0),
                           0,
                           0)
        else:
            #self.setSceneRect(0, 0, 297 / (25.4 / 96), 210 / (25.4 / 96))
            self.getCurrentPageScene().addBorder(272 / (25.4 / 96.0),
                           177 / (25.4 / 96.0),
                           ((297-272) / 2) / (25.4 / 96.0),
                           0,
                           19 / (25.4 / 96.0),
                           0)

    def exitApp(self):
        print("exit app")
        qm = QMessageBox()
        ret = qm.question(self, 'Exit', "Are you sure you want to exit the application?", qm.Yes | qm.No)

        if ret == qm.No:
            return

        self.close()

    def _createMenuBar(self):
        menuBar = self.menuBar()
        # Creating menus using a QMenu object
        fileMenu = QMenu(_("&File"), self)
        menuBar.addMenu(fileMenu)
        fileMenu.addAction(self.newAction)
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.saveAction)
        fileMenu.addAction(self.printAction)
        fileMenu.addAction(self.printPreviewAction)
        fileMenu.addAction(self.printPDFAction)
        fileMenu.addAction(self.exitAction)
        # Creating menus using a title
        editMenu = menuBar.addMenu(_("&Edit"))
        editMenu.addAction(self.copyAction)
        editMenu.addAction(self.pasteAction)
        editMenu.addAction(self.cutAction)
        # stamp menu
        stampMenu = menuBar.addMenu(_("&Stamp"))
        stampMenu.addAction(self.newStampAction)
        stampMenu.addAction(self.editStampAction)

        # align menu
        alignMenu = menuBar.addMenu(_("Align"))
        alignMenu.addAction(self.alignLeftAction)
        alignMenu.addAction(self.alignRightAction)
        alignMenu.addAction(self.alignTopAction)
        alignMenu.addAction(self.alignBottomAction)
        alignMenu.addAction(self.centerHorizontallyAction)
        alignMenu.addAction(self.centerVerticallyAction)
        alignMenu.addAction(self.distributeVerticallyAction)
        alignMenu.addAction(self.distributeHorizontallyAction)

        # page menu
        pageMenu = menuBar.addMenu(_("Page"))
        pageMenu.addAction(self.newPageAction)
        pageMenu.addAction(self.deletePageAction)
        pageMenu.addAction(self.drawGridAction)
        pageMenu.addAction(self.deleteAlbumAction)

        # object menu
        objectMenu = menuBar.addMenu(_("Objects"))
        objectMenu.addAction(self.newTextAction)
        objectMenu.addAction(self.newImageAction)
        objectMenu.addAction(self.newBorderAction)
        objectMenu.addAction(self.newCopyRightAction)
        objectMenu.addAction(self.newCopyRightAllPagesAction)
        objectMenu.addAction(self.newPageNbrAction)
        objectMenu.addAction(self.newPageNbrAllPagesAction)

        # Config menu
        configMenu = menuBar.addMenu(_("&Config"))
        configMenu.addAction(self.setupAppAction)

        # help menu
        helpMenu = menuBar.addMenu(_("&Help"))
        helpMenu.addAction(self.helpContentAction)
        helpMenu.addAction(self.aboutAction)

    def _createActions(self):
        # Creating action
        # New
        self.newAction = QAction(self)
        self.newAction.setText(_("&New"))
        iconNew = QIcon()
        iconNew.addPixmap(QPixmap("images/new.png"), QIcon.Normal, QIcon.Off)
        self.newAction.setIcon(iconNew)

        # Open
        self.openAction = QAction(_("&Open..."), self)
        iconOpen = QIcon()
        iconOpen.addPixmap(QPixmap("images/open.png"), QIcon.Normal, QIcon.Off)
        self.openAction.setIcon(iconOpen)
        self.openAction.setObjectName("actionOpen")

        # Save
        self.saveAction = QAction(_("&Save"), self)
        iconSave = QIcon()
        iconSave.addPixmap(QPixmap("images/save.png"), QIcon.Normal, QIcon.Off)
        self.saveAction.setIcon(iconSave)
        self.saveAction.setObjectName("actionSave")

        # print actions
        self.printAction = QAction(_("&Print..."), self)
        iconPrint = QIcon()
        iconPrint.addPixmap(QPixmap("images/print.png"), QIcon.Normal, QIcon.Off)
        self.printAction.setIcon(iconPrint)
        self.printAction.setObjectName("printAction")

        # print preview
        self.printPreviewAction = QAction(_("&Print preview..."), self)
        iconPrintPreview = QIcon()
        iconPrintPreview.addPixmap(QPixmap("images/printprev.png"), QIcon.Normal, QIcon.Off)
        self.printPreviewAction.setIcon(iconPrintPreview)
        self.printPreviewAction.setObjectName("printPreviewAction")

        # print PDF
        self.printPDFAction = QAction(_("&Print PDF..."), self)
        iconPrintPDF = QIcon()
        iconPrintPDF.addPixmap(QPixmap("images/pdf.png"), QIcon.Normal, QIcon.Off)
        self.printPDFAction.setIcon(iconPrintPDF)
        self.printPDFAction.setObjectName("printPDFAction")

        # exit
        self.exitAction = QAction(_("&Exit"), self)
        iconExit = QIcon()
        iconExit.addPixmap(QPixmap("images/exit.png"), QIcon.Normal, QIcon.Off)
        self.exitAction.setIcon(iconExit)
        self.exitAction.setObjectName("exitAction")

        # Edit actions
        self.copyAction = QAction(_("&Copy"), self)
        iconCopy = QIcon()
        iconCopy.addPixmap(QPixmap("images/copy.png"), QIcon.Normal, QIcon.Off)
        self.copyAction.setIcon(iconCopy)

        self.pasteAction = QAction(_("&Paste"), self)
        iconPaste = QIcon()
        iconPaste.addPixmap(QPixmap("images/paste.png"), QIcon.Normal, QIcon.Off)
        self.pasteAction.setIcon(iconPaste)


        self.cutAction = QAction(_("C&ut"), self)
        iconCut = QIcon()
        iconCut.addPixmap(QPixmap("images/cut.png"), QIcon.Normal, QIcon.Off)
        self.cutAction.setIcon(iconCut)

        # stamp actions
        self.newStampAction = QAction(_("New Stamp ..."), self)
        self.editStampAction = QAction(_("Edit Current Stamp ..."), self)
        stampIcon = QIcon()
        stampIcon.addPixmap(QPixmap("images/stamp.png"), QIcon.Normal, QIcon.Off)
        self.newStampAction.setIcon(stampIcon)
        # todo add icon

        # pages action
        self.newPageAction = QAction(_("New Page ..."), self)
        iconNewPage  = QIcon()
        iconNewPage.addPixmap(QPixmap("images/page.png"), QIcon.Normal, QIcon.Off)
        self.newPageAction.setIcon(iconNewPage)

        self.deletePageAction = QAction(_("Delete Page ..."), self)
        iconDeletePage  = QIcon()
        iconDeletePage.addPixmap(QPixmap("images/delete_page.png"), QIcon.Normal, QIcon.Off)
        self.deletePageAction.setIcon(iconDeletePage)

        self.drawGridAction = QAction(_("Grid on/off"), self)
        iconDrawGrid  = QIcon()
        iconDrawGrid.addPixmap(QPixmap("images/grid.png"), QIcon.Normal, QIcon.Off)
        self.drawGridAction.setIcon(iconDrawGrid)

        self.deleteAlbumAction = QAction(_("Delete Album ..."), self)
        iconDelete = QIcon()
        iconDelete.addPixmap(QPixmap("images/trash.png"), QIcon.Normal, QIcon.Off)
        self.deleteAlbumAction.setIcon(iconDelete)


        # object action
        self.newTextAction = QAction(_("New text ..."), self)
        iconNewText  = QIcon()
        iconNewText.addPixmap(QPixmap("images/text.png"), QIcon.Normal, QIcon.Off)
        self.newTextAction.setIcon(iconNewText)

        self.newImageAction = QAction(_("New Image ..."), self)
        iconNewImage  = QIcon()
        iconNewImage.addPixmap(QPixmap("images/image.png"), QIcon.Normal, QIcon.Off)
        self.newImageAction.setIcon(iconNewImage)

        self.newCopyRightAction = QAction(_("New copyright"), self)
        iconCopyright = QIcon()
        iconCopyright.addPixmap(QPixmap("images/copyright.png"), QIcon.Normal, QIcon.Off)
        self.newCopyRightAction.setIcon(iconCopyright)

        self.newCopyRightAllPagesAction = QAction(_("New copyright all pages"), self)
        iconCopyrightAllPages = QIcon()
        iconCopyrightAllPages.addPixmap(QPixmap("images/page_copyright.png"), QIcon.Normal, QIcon.Off)
        self.newCopyRightAllPagesAction.setIcon(iconCopyrightAllPages)

        self.newBorderAction = QAction(_("New Page border"), self)
        iconNewBorder = QIcon()
        iconNewBorder.addPixmap(QPixmap("images/border.png"), QIcon.Normal, QIcon.Off)
        self.newBorderAction.setIcon(iconNewBorder)

        self.newPageNbrAction = QAction(_("New page nbr"), self)
        iconPageNbr = QIcon()
        iconPageNbr.addPixmap(QPixmap("images/number.png"), QIcon.Normal, QIcon.Off)
        self.newPageNbrAction.setIcon(iconPageNbr)

        self.newPageNbrAllPagesAction = QAction(_("New page nbr all pages"), self)
        iconPageNbrAllPages = QIcon()
        iconPageNbrAllPages.addPixmap(QPixmap("images/number.png"), QIcon.Normal, QIcon.Off)
        self.newPageNbrAllPagesAction.setIcon(iconPageNbrAllPages)

        # align actions
        self.alignLeftAction = QAction(_("Align Left"), self)
        iconAlignLeft = QIcon()
        iconAlignLeft.addPixmap(QPixmap("images/align_left.png"), QIcon.Normal, QIcon.Off)
        self.alignLeftAction.setIcon(iconAlignLeft)

        self.alignRightAction = QAction(_("Align Right"), self)
        iconAlignRight = QIcon()
        iconAlignRight.addPixmap(QPixmap("images/align_right.png"), QIcon.Normal, QIcon.Off)
        self.alignRightAction.setIcon(iconAlignRight)

        self.alignTopAction = QAction(_("Align Top"), self)
        iconAlignTop = QIcon()
        iconAlignTop.addPixmap(QPixmap("images/align_top.png"), QIcon.Normal, QIcon.Off)
        self.alignTopAction.setIcon(iconAlignTop)

        self.alignBottomAction = QAction(_("Align Bottom"), self)
        iconAlignBottom = QIcon()
        iconAlignBottom.addPixmap(QPixmap("images/align_bottom.png"), QIcon.Normal, QIcon.Off)
        self.alignBottomAction.setIcon(iconAlignBottom)

        self.distributeVerticallyAction = QAction(_("Distribute Vertically"), self)
        iconDistributeVertically = QIcon()
        iconDistributeVertically.addPixmap(QPixmap("images/distribute_vertical.png"), QIcon.Normal, QIcon.Off)
        self.distributeVerticallyAction.setIcon(iconDistributeVertically)

        self.distributeHorizontallyAction = QAction(_("Distribute Horizontally"), self)
        iconDistributeHorizontally = QIcon()
        iconDistributeHorizontally.addPixmap(QPixmap("images/distribute_horiz.png"), QIcon.Normal, QIcon.Off)
        self.distributeHorizontallyAction.setIcon(iconDistributeHorizontally)

        self.centerHorizontallyAction = QAction(_("Center Horizontally"), self)
        iconCenterHorizontally = QIcon()
        iconCenterHorizontally.addPixmap(QPixmap("images/center_horizontal.png"), QIcon.Normal, QIcon.Off)
        self.centerHorizontallyAction.setIcon(iconCenterHorizontally)

        self.centerVerticallyAction = QAction(_("Center Vertically"), self)
        iconCenterVertically = QIcon()
        iconCenterVertically.addPixmap(QPixmap("images/center_vertical.png"), QIcon.Normal, QIcon.Off)
        self.centerVerticallyAction.setIcon(iconCenterVertically)

        # config action
        self.setupAppAction = QAction(_("Setup application"), self)
        iconSetup = QIcon()
        iconSetup.addPixmap(QPixmap("images/config.png"), QIcon.Normal, QIcon.Off)
        self.setupAppAction.setIcon(iconSetup)

        # help actions
        self.helpContentAction = QAction(_("&Help Content"), self)
        iconHelp = QIcon()
        iconHelp.addPixmap(QPixmap("images/help.png"), QIcon.Normal, QIcon.Off)
        self.helpContentAction.setIcon(iconHelp)

        self.aboutAction = QAction(_("&About"), self)
        iconAbout = QIcon()
        iconAbout.addPixmap(QPixmap("images/about.png"), QIcon.Normal, QIcon.Off)
        self.aboutAction.setIcon(iconAbout)

    def _createToolBars(self):
        # File toolbar
        fileToolBar = self.addToolBar("File")
        fileToolBar.addAction(self.newAction)
        fileToolBar.addAction(self.openAction)
        fileToolBar.addAction(self.saveAction)
        fileToolBar.addAction(self.printPDFAction)
        fileToolBar.addAction(self.printPreviewAction)
        fileToolBar.addAction(self.exitAction)

        # Edit toolbar
        editToolBar = QToolBar("Edit", self)
        editToolBar.addAction(self.copyAction)
        editToolBar.addAction(self.pasteAction)
        editToolBar.addAction(self.cutAction)
        self.addToolBar(editToolBar)

        # page toolbar
        pageToolBar = QToolBar("Page", self)
        pageToolBar.addAction(self.newPageAction)
        pageToolBar.addAction(self.deletePageAction)
        pageToolBar.addAction(self.drawGridAction)
        pageToolBar.addAction(self.deleteAlbumAction)
        self.addToolBar(pageToolBar)

        # align toolbar
        alignToolBar = QToolBar("Align", self)
        alignToolBar.addAction(self.alignLeftAction)
        alignToolBar.addAction(self.alignRightAction)
        alignToolBar.addAction(self.alignTopAction)
        alignToolBar.addAction(self.alignBottomAction)
        alignToolBar.addAction(self.distributeVerticallyAction)
        alignToolBar.addAction(self.distributeHorizontallyAction)
        alignToolBar.addAction(self.centerHorizontallyAction)
        alignToolBar.addAction(self.centerVerticallyAction)
        self.addToolBar(alignToolBar)
        self.addToolBarBreak()

        # stamp toolbar
        stampToolBar = QToolBar("Stamp", self)
        stampToolBar.addAction(self.newStampAction)
        self.addToolBar(stampToolBar)

        # objects toolbar
        objectToolBar = QToolBar("Objects", self)
        objectToolBar.addAction(self.newTextAction)
        self.addToolBar(objectToolBar)

        # Help QToolBar
        helpToolBar = QToolBar("Help", self)
        helpToolBar.addAction(self.helpContentAction)
        helpToolBar.addAction(self.aboutAction)
        helpToolBar.addAction(self.setupAppAction)
        self.addToolBar(helpToolBar)

        # status bar
        statusBar = QStatusBar(self)
        statusBar.setObjectName("statusBar")
        self.setStatusBar(statusBar)

    def _connectActions(self):
        # Connect File actions
        self.newAction.triggered.connect(self.newFile)
        # self.openAction.triggered.connect(self.openFile)
        self.openAction.triggered.connect(self.openAlbumFile)
        # self.saveAction.triggered.connect(self.saveFile)
        self.saveAction.triggered.connect(self.saveAlbumToFile)
        self.printAction.triggered.connect(self.printAllPagesPDF)
        self.printPDFAction.triggered.connect(self.printPagePDF)
        self.printPreviewAction.triggered.connect(self.printPreviewAllPages)
        self.printAction.triggered.connect(self.printPage)

        self.exitAction.triggered.connect(self.exitApp)

        # edit actions
        self.copyAction.triggered.connect(self.copy)
        self.cutAction.triggered.connect(self.cut)
        self.pasteAction.triggered.connect(self.paste)

        # align actions
        self.alignBottomAction.triggered.connect(self.alignBottom)
        self.alignTopAction.triggered.connect(self.alignTop)
        self.alignLeftAction.triggered.connect(self.alignLeft)
        self.alignRightAction.triggered.connect(self.alignRight)
        self.distributeHorizontallyAction.triggered.connect(self.distributeHorizontally)
        self.distributeVerticallyAction.triggered.connect(self.distributeVertically)
        self.centerVerticallyAction.triggered.connect(self.centerVertically)
        self.centerHorizontallyAction.triggered.connect(self.centerHorizontally)
        # config actions
        self.setupAppAction.triggered.connect(self.configApp)

        # stamp actions
        self.newStampAction.triggered.connect(self.createNewStamp)
        self.editStampAction.triggered.connect(self.editStamp)

        # page actions
        self.newPageAction.triggered.connect(self.newPage)
        self.deletePageAction.triggered.connect(self.deleteCurrentPage)
        self.drawGridAction.triggered.connect(self.gridOnOff)
        self.deleteAlbumAction.triggered.connect(self.deleteAlbum)

        # objects actions
        self.newTextAction.triggered.connect(self.createText)
        self.newCopyRightAction.triggered.connect(self.newCopyRight)
        self.newCopyRightAllPagesAction.triggered.connect(self.newCopyRightAllPages)
        self.newImageAction.triggered.connect(self.newImage)
        self.newBorderAction.triggered.connect(self.newBorder)
        self.newPageNbrAction.triggered.connect(self.newPageNbr)
        self.newPageNbrAllPagesAction.triggered.connect(self.newPageNbrAllPages)

        # help actions
        self.aboutAction.triggered.connect(self.about)
        self.helpContentAction.triggered.connect(self.help)

    # file menu functions
    # delete all pages and create a new file
    def newFile(self):
        # Logic for creating a new file goes here...
        print("creating new File")
        # Ask user about confirmation on deleting all pages
        qm = QMessageBox()
        ret = qm.question(self, '', _("Are you sure you want to delete all the pages?"), qm.Yes | qm.No)

        if ret == qm.No:
            return
        # Delete all pages
        self.deleteAllPages()
        # Create one empty page
        self.newPage(None, True)

    def newPageNbr(self):
        print("")
        self.getCurrentPageScene().newPageNbr()

    def newPageNbrAllPages(self):
        print("Create new  nbr")
        dlg = TextDlg()
        res = dlg.exec_()

        if res == QDialog.Accepted:
            print("Clicked ok")
            text = dlg.eTXT.toPlainText()
            font = dlg.eTXT.font()
            align = dlg.eTXT.alignment()

            for x in range(0, self.tabs.count().real):
                #self.tabs.removeTab(self.tabs.currentIndex())
                self.tabs.setCurrentIndex(x)
                self.getCurrentPageScene().addPageNbr(text + " " + str(self.tabs.currentIndex() + 1))

        if res == QDialog.Rejected:
            print("Clicked cancel")

    # open an album from a file
    def openAlbumFile(self):
        print("Open album")
        qm = QMessageBox()
        ret = qm.question(self, '', "Are you sure you want to delete all the pages?", qm.Yes | qm.No)

        if ret == qm.No:
            return

        # first delete all pages
        self.deleteAllPages()

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        #fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
        #                                          "Album Files (*.sta);Xml Files (*.xml)", options=options)
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "Album Files (*.sta)", options=options)
        if fileName:
            print(fileName)
            fileNameArray = fileName.split(".")
            print(fileNameArray[1])
            print(len(fileNameArray))
        else:
            return

        #if (fileNameArray[1]=="sta"):
        if (fileNameArray[len(fileNameArray)-1] == "sta"):
            f = gzip.open(fileName, 'r')
        else:
            f = open(fileName, 'r')
        #mytree = ET.parse(fileName)
        mytree = ET.parse(f)
        f.close()
        myroot = mytree.getroot()
        #print(myroot)
        for it in myroot.findall('page'):
            #print("before")
            #print(it.attrib.get("type"))
            #print("after")
            # create new page
            self.newPage(str(it.attrib.get("type")), False)
            print("after page created")
            # get the current page
            currentPage = self.getCurrentPageScene()
            # Open the text label
            textLabelsItems = it.findall('textLabel')
            for textLabel in textLabelsItems:
                #print("labels!!")
                label = textLabel.find('label').text

                font = textLabel.find('font')
                bold = font.find('bold').text
                underline = font.find('underline').text
                italic = font.find('italic').text
                strikeOut = font.find('strikeOut').text
                pointSize = font.find('pointSize').text

                myFont = QFont()
                myFont.setBold(self.str_to_bool(bold))
                myFont.setUnderline(self.str_to_bool(underline))
                myFont.setItalic(self.str_to_bool(italic))
                myFont.setStrikeOut(self.str_to_bool(strikeOut))
                myFont.setPointSize(int(pointSize))


                pos = textLabel.find('labelPos')
                x = pos.find('x').text
                y = pos.find('y').text

                currentPage.addTextLabel(label, float(x), float(y), myFont)

            copyrightLabelsItems = it.findall('labelCopyRight')
            for copyrightLabel in copyrightLabelsItems:
                # print("labels!!")
                label = copyrightLabel.find('label').text

                font = copyrightLabel.find('font')
                bold = font.find('bold').text
                underline = font.find('underline').text
                italic = font.find('italic').text
                strikeOut = font.find('strikeOut').text
                pointSize = font.find('pointSize').text

                myFont = QFont()
                myFont.setBold(self.str_to_bool(bold))
                myFont.setUnderline(self.str_to_bool(underline))
                myFont.setItalic(self.str_to_bool(italic))
                myFont.setStrikeOut(self.str_to_bool(strikeOut))
                myFont.setPointSize(int(pointSize))

                pos = copyrightLabel.find('labelPos')
                x = pos.find('x').text
                y = pos.find('y').text

                currentPage.addTextLabel(label, float(x), float(y), myFont, Qt.AlignLeft, "labelCopyRight")

            yearLabelsItems = it.findall('labelYear')
            for yearLabel in yearLabelsItems:
                # print("year labels!!")
                label = yearLabel.find('label').text

                font = yearLabel.find('font')
                bold = font.find('bold').text
                underline = font.find('underline').text
                italic = font.find('italic').text
                strikeOut = font.find('strikeOut').text
                pointSize = font.find('pointSize').text

                myFont = QFont()
                myFont.setBold(self.str_to_bool(bold))
                myFont.setUnderline(self.str_to_bool(underline))
                myFont.setItalic(self.str_to_bool(italic))
                myFont.setStrikeOut(self.str_to_bool(strikeOut))
                myFont.setPointSize(int(pointSize))

                pos = yearLabel.find('labelPos')
                x = pos.find('x').text
                y = pos.find('y').text

                currentPage.addTextLabel(label, float(x), float(y), myFont, Qt.AlignCenter, "labelYear")

            # open the page border
            pageBorderItem = it.findall('borderGroup')
            for border in pageBorderItem:
                print("Page border!!")
                pos = border.find('borderPos')
                x = pos.find('x').text
                print(x)
                y = pos.find('y').text
                print(y)
                width1 = border.find('width1').text
                print(width1)
                height1 = border.find('height1').text
                print(height1)
                # print(currentPage.getPageName)
                currentPage.addBorder(float(width1), float(height1),
                                      float(x), float(y), 0, 0)

            # Open the Stamps
            stampItems = it.findall('stampGroup')
            for stamp in stampItems:
                print("stamps!!")
                print(stamp)
                #print(stamp.stampPos)
                pos = stamp.find('stampPos')
                x = pos.find('x').text
                print(x)
                y = pos.find('y').text
                print(y)

                sizeBox = stamp.find('stampBox')
                width = sizeBox.find('width').text
                print(width)
                height = sizeBox.find('height').text
                print(height)
                try:
                    stampBox_width = sizeBox.find('stampBox_width').text
                    print(stampBox_width)
                    stampBox_height = sizeBox.find('stampBox_height').text
                    print(stampBox_height)
                    use_new = 1
                except:
                    print("An exception occurred")
                    use_new = 0

                stampDesc = stamp.find('stampDesc').text
                print(stampDesc)

                if stampDesc is None:
                    stampDesc = ""
                stampNbr = stamp.find('stampNbr').text
                print(stampNbr)
                stampValue = stamp.find('stampValue').text
                print(stampValue)
                print("after Value")
                try:
                    pixmapitem = stamp.find('pixmapItem').text
                except:
                    print("An exception occurred")
                print("before stamp")
                stamp = Stamp()
                print("before pix")

                #print(pixmapitem)
                pixmap = self.bytesToPixmap(pixmapitem)
                #pixmap = self.bytesToPixmap2(pixmapitem)
                #print("after pix")
                #stamp.createStampPix(currentPage, str(stampNbr), str(stampValue), str(stampDesc),
                #                     float(width) * (25.4 / 96.0), float(height) * (25.4 / 96.0),
                #                     float(x), float(y), pixmap)

                if use_new == 1:
                    stamp.createStampPix(currentPage, str(stampNbr), str(stampValue), str(stampDesc),
                                        float(stampBox_width), float(stampBox_height),
                                        float(x), float(y), pixmap)
                else:
                    stamp.createStampPix(currentPage, str(stampNbr), str(stampValue), str(stampDesc),
                                        float(width) * (25.4 / 96.0), float(height) * (25.4 / 96.0),
                                        float(x), float(y), pixmap)
                print("after stamp")
    # save an album to a file
    def saveAlbumToFile(self):
        print("Save album to file")

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                  "Album Files (*.sta)", options=options)
        if fileName:
            print(fileName)
            if fileName.find(".") != -1:
                fileNameArray = fileName.split(".")
                print(fileNameArray[1])
                print(len(fileNameArray))
                if (fileNameArray[len(fileNameArray) - 1] == "sta"):
                    print(fileName.rsplit('.', maxsplit=1)[0])
                    fileName = fileName.rsplit('.', maxsplit=1)[0]
        else:
            return



        root = ET.Element("album")

        for x in range(self.tabs.count()):
            self.tabs.setCurrentIndex(x)

            currentScene = self.getCurrentPageScene()
            page = ET.SubElement(root, "page", name="%s" % x, type="%s" % currentScene.pageType)

            items = currentScene.items()
            for item in items:
                if item.type().real == 8:
                    par = item.parentItem()
                    # exclude all item where parent is a group
                    if par is None:
                        textLbl = ET.SubElement(page, item.data(0))
                        ET.SubElement(textLbl, "label").text = item.toPlainText()

                        font = ET.SubElement(textLbl, "font")
                        ET.SubElement(font, "bold").text = str(item.font().bold())
                        ET.SubElement(font, "underline").text = str(item.font().underline())
                        ET.SubElement(font, "italic").text = str(item.font().italic())
                        ET.SubElement(font, "strikeOut").text = str(item.font().strikeOut())
                        ET.SubElement(font, "pointSize").text = str(item.font().pointSize())

                        pos = ET.SubElement(textLbl, "labelPos")
                        ET.SubElement(pos, "x").text = str(item.x())
                        ET.SubElement(pos, "y").text = str(item.y())

                elif item.type().real == 10 and item.data(0) == "borderGroup":
                    print("border group")
                    border = ET.SubElement(page, item.data(0))
                    borderItems = item.childItems()
                    pos = ET.SubElement(border, "borderPos")
                    ET.SubElement(pos, "x").text = str(item.x())
                    ET.SubElement(pos, "y").text = str(item.y())
                    i = 0
                    for borderItem in borderItems:
                        if borderItem.type().real == 3:
                            i = i + 1

                            # ET.SubElement(border, "width" + str(i)).text = str(
                            #     borderItem.boundingRect().width())
                            # ET.SubElement(border, "height" + str(i)).text = str(
                            #     borderItem.boundingRect().height())
                            ET.SubElement(border, "width" + str(i)).text = str(borderItem.data(1))
                            ET.SubElement(border, "height" + str(i)).text = str(borderItem.data(2))

                elif item.type().real == 10 and item.data(0) == "stampGroup":
                    #print("dta0:%s" % item.data(0))
                    stamp = ET.SubElement(page, item.data(0))
                    stampItems = item.childItems()

                    pos = ET.SubElement(stamp, "stampPos")
                    ET.SubElement(pos, "x").text = str(item.x())
                    ET.SubElement(pos, "y").text = str(item.y())
                    for stampItem in stampItems:
                        #print(stampItem.data(0))
                        # if it is a textBox child
                        if stampItem.type().real == 8:
                            ET.SubElement(stamp, stampItem.data(0)).text = stampItem.toPlainText()
                        # This is the pixmap
                        elif stampItem.type().real == 7:
                            pix = stampItem.pixmap()
                            #print(self.pixmapToBytes(pix))
                            ET.SubElement(stamp, stampItem.data(0)).text = str(self.pixmapToBytes(pix))
                        # This is the stamp box
                        elif stampItem.type().real == 3:
                            #print(stampItem.boundingRect().width())
                            size = ET.SubElement(stamp, stampItem.data(0))
                            ET.SubElement(size, "width").text = str(stampItem.boundingRect().width())
                            ET.SubElement(size, "height").text = str(stampItem.boundingRect().height())
                            ET.SubElement(size, "stampBox_width").text = str(int(stampItem.data(1)))
                            ET.SubElement(size, "stampBox_height").text = str(int(stampItem.data(2)))

        print("finished")
        tree = ET.ElementTree(root)

        tree.write(fileName)

        f = gzip.open(fileName + '.sta', 'wb')
        ET.ElementTree(root).write(f)
        f.close()
        # delete uncompressed file
        if os.path.isfile(fileName):
            os.remove(fileName)

    # print all pages
    def printAllPagesPDF(self):
        print("print all pages")
        printer = QPrinter(QPrinter.HighResolution)
        printer.setPageSize(QtGui.QPagedPaintDevice.A4)
        printer.setOutputFormat(QPrinter.PdfFormat)

        # TODO select the file to print
        printer.setOutputFileName("album4.pdf")
        scale = printer.resolution() / 96.0

        printer.setPageMargins(0, 0, 0, 0, QPrinter.Unit.Millimeter)
        p = QPainter(printer)
        for x in range(self.tabs.count()):
            self.tabs.setCurrentIndex(x)
            currentScene = self.getCurrentPageScene()

            # first unselect all objects
            for item in currentScene.items():
                item.setSelected(False)

            if currentScene.pageType == "portrait":
                printer.setPageOrientation(0)
                print("Portrait")
            else:
                printer.setPageOrientation(1)
                print("Landscape")
            if x > 0:
                printer.newPage()

            source = QtCore.QRectF(0, 0, currentScene.width(), currentScene.height())
            target = QRectF(0, 0, source.size().width() * scale, source.size().height() * scale)

            currentScene.render(p, target, source)


        p.end()

    # print all pages
    def printPreviewAllPagesOld(self):
        print("print all pages")
        previewDialog = QPrintPreviewDialog()

        previewDialog.printer().setResolution(QPrinter.HighResolution)
        previewDialog.printer().setOutputFormat(QPrinter.PdfFormat)
        previewDialog.printer().setPageSize(QtGui.QPagedPaintDevice.A4)
        previewDialog.exec_()

        # TODO select the file to print
        #printer.setOutputFileName("album4.pdf")
        scale = previewDialog.printer().resolution() / 96.0

        previewDialog.printer().setPageMargins(0, 0, 0, 0, QPrinter.Unit.Millimeter)
        p = QPainter(previewDialog.printer())
        for x in range(self.tabs.count()):
            self.tabs.setCurrentIndex(x)
            currentScene = self.getCurrentPageScene()

            # first unselect all objects
            for item in currentScene.items():
                item.setSelected(False)

            if currentScene.pageType == "portrait":
                previewDialog.printer().setPageOrientation(0)
                print("Portrait")
            else:
                previewDialog.printer().setPageOrientation(1)
                print("Landscape")
            if x > 0:
                previewDialog.printer().newPage()

            source = QtCore.QRectF(0, 0, currentScene.width(), currentScene.height())
            target = QRectF(0, 0, source.size().width() * scale, source.size().height() * scale)

            currentScene.render(p, target, source)

        p.end()

    # print all pages
    def printPreviewAllPages(self):
        print("print all pages")
        previewDialog = QPrintPreviewDialog()

        previewDialog.printer().setResolution(QPrinter.HighResolution)
        previewDialog.printer().setOutputFormat(QPrinter.PdfFormat)
        previewDialog.printer().setPageSize(QtGui.QPagedPaintDevice.A4)

        previewDialog.paintRequested.connect(self.createPreview)

        previewDialog.exec_()

    def createPreview(self, printer):
        scale = printer.resolution() / 96.0
        printer.setPageMargins(0, 0, 0, 0, QPrinter.Unit.Millimeter)

        p = QPainter(printer)
        for x in range(self.tabs.count()):
            self.tabs.setCurrentIndex(x)

            currentScene = self.getCurrentPageScene()

            if currentScene.pageType == "portrait":
                printer.setPageOrientation(0)
            else:
                printer.setPageOrientation(1)

            if x > 0:
                printer.newPage()

            # first unselect all objects
            for item in currentScene.items():
                item.setSelected(False)

            source = QtCore.QRectF(0, 0, currentScene.width(), currentScene.height())
            target = QRectF(0, 0, source.size().width() * scale, source.size().height() * scale)

            currentScene.render(p, target, source)

        p.end()

    # print current page and save it to PDF
    def printPagePDF(self):
        print("print to PDF")
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName2, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "album.pdf",
                                                   "(*.pdf)", options=options)
        print("Save album to file3")
        if fileName2:
            print(fileName2)
        else:
            return
        self.getCurrentPageScene().printPagePDF(fileName2)

    # print preview the current page
    def printPreview(self):
        print("Print preview page")
        self.getCurrentPageScene().printPreview()

    # review !!!!
    def printPage(self):
        print("Print page")


        # printer.setPageSize(QtGui.QPagedPaintDevice.A4)
        # printer.setResolution(100)
        #
        # painter = QtGui.QPainter(printer)
        # delta = 20
        # f = painter.font()
        # f.setPixelSize(delta)
        # painter.setFont(f)
        #
        # target = QtCore.QRectF(0, 0, printer.width(), 0)
        #
        # print(printer.width())
        # print(printer.height())

        # for item in self.page.scene.items():
        #     #source = item.mapToScene(item.boundingRect()).boundingRect()
        #     source = item.boundingRect()
        #     print("item size")
        #     print(source.height())
        #     print(source.width())
        #
        #     target.setHeight(source.height())
        #     if target.bottom() > printer.height():
        #         printer.newPage()
        #         target.moveTop(0)
        #     self.page.scene.render(painter, target, source)
        # if item.type().real == 8:
        #     print("type 8")
        #     par = item.parentItem()
        #     # exclude all item where parent is a group
        #     if par is None:
        #         self.page.scene.render(painter, target, source)
        # elif item.type().real == 10:
        #     print("type 10")
        #     self.page.scene.render(painter, target, source)

        # stampItems = item.childItems()
        # for stampItem in stampItems:

        # f = painter.font()
        # f.setPixelSize(delta)
        # painter.drawText(
        #     QtCore.QRectF(
        #         target.bottomLeft(), QtCore.QSizeF(printer.width(), delta + 5)
        #     ),
        #     "test",
        # )
        # painter.end()

    # need to be written !!!
    def importFileFromExcel(self):
        print("import file from Excel")

    # edit menu functions
    # copy selected object(s)
    def copy(self):
        self.getCurrentPage().copy_items()

    # cut selected object(s)
    def cut(self):
        self.getCurrentPage().copy_items()
        self.getCurrentPageScene().removeItems()

    # paste objects that have been copied or cut to the current page
    def paste(self):
        self.getCurrentPage().paste_items()

    # stamp menu functions
    def createNewStamp(self):
        print("creating new stamp")
        stamp = self.getCurrentPageScene().newStamp(self.lastStampObj)
        if stamp is not None:
            self.lastStampObj['year'] = stamp['year']
            self.lastStampObj['type'] = stamp['type']
            self.lastStampObj['country'] = stamp['country']
            self.lastStampObj['nbr'] = stamp['nbr']

    # edit current selected stamp
    def editStamp(self):
        self.getCurrentPageScene().editObject()

    # help menu functions
    # about the application
    def about(self):
        aboutMsg = QMessageBox()
        aboutMsg.setWindowTitle(_("About Stamp Album"))
        aboutMsg.setText(_("Stamp Album ver5.0.1 \n Copyright Boris du Reau 2003-2023"))
        aboutMsg.setIcon(QMessageBox.Information)
        aboutMsg.exec_()

    # application on line help
    def help(self):
        #os.system('xdg-open ' + "Help/StampAlbum Manuel utilisateur 01-08-2023.pdf")
        #os.startfile("Help/StampAlbum Manuel utilisateur 01-08-2023.pdf")
        if sys.platform.startswith('win32'):
            os.startfile("Help\\StampAlbum Manuel utilisateur 01-08-2023.pdf")
        # dlg = HelpDlg()
        # res = dlg.exec_()
        #
        # if res == QDialog.Accepted:
        #     print("Clicked ok")

    # align menu functions
    def alignBottom(self):
        self.getCurrentPageScene().alignBottom()

    def alignTop(self):
        self.getCurrentPageScene().alignTop()

    def alignLeft(self):
        self.getCurrentPageScene().alignLeft()

    def alignRight(self):
        self.getCurrentPageScene().alignRight()

    def distributeHorizontally(self):
        self.getCurrentPageScene().distributeHorizontally()

    def distributeVertically(self):
        self.getCurrentPageScene().distributeVertically()

    def centerHorizontally(self):
        self.getCurrentPageScene().centerHorizontally()

    def centerVertically(self):
        self.getCurrentPageScene().centerVertically()

    # misc functions
    def createText(self):
        print("create text")
        self.getCurrentPageScene().newLabel()

    # turn the grid on and off
    def gridOnOff(self):
        child = self.getCurrentPageScene()
        if self.gridOn:
            child.setBackgroundBrush(QBrush(self.deleteGrid()))
            self.gridOn = False
        else:
            child.setBackgroundBrush(QBrush(self.drawGrid()))
            self.gridOn = True

    # used to draw the grid
    def drawGrid(self):
        self.pixmap = QPixmap(10, 10)
        pixmapWidth = self.pixmap.width() - 1
        painter = QPainter()

        self.pixmap.fill(Qt.transparent)

        painter.begin(self.pixmap)
        painter.setPen(Qt.gray)
        painter.drawLine(0, 0, pixmapWidth, 0)
        painter.drawLine(0, 0, 0, pixmapWidth)
        return self.pixmap

    # used to delete the grid
    def deleteGrid(self):
        self.pixmap = QPixmap(10, 10)
        pixmapWidth = self.pixmap.width() - 1
        painter = QPainter()

        self.pixmap.fill(Qt.transparent)

        painter.begin(self.pixmap)
        painter.setPen(Qt.white)
        painter.drawLine(0, 0, pixmapWidth, 0)
        painter.drawLine(0, 0, 0, pixmapWidth)
        return self.pixmap

    def pixmapToBytes(self, pixmap):
        # convert QPixmap to bytes
        ba = QtCore.QByteArray()
        buff = QtCore.QBuffer(ba)
        buff.open(QtCore.QIODevice.WriteOnly)
        ok = pixmap.save(buff, "PNG")
        assert ok
        return bytes(ba.toBase64()).decode()

    def bytesToPixmap(self, pixmap_bytes):
        # convert bytes to QPixmap
        ba = QtCore.QByteArray().fromBase64(pixmap_bytes.encode())
        pixmap = QtGui.QPixmap()
        ok = pixmap.loadFromData(ba, "PNG")
        assert ok
        return pixmap

    def bytesToPixmap2(self, pixmap_bytes):
        # convert bytes to QPixmap
        ba = QtCore.QByteArray().fromBase64(pixmap_bytes.encode())
        pixmap = QtGui.QPixmap()
        ok = pixmap.loadFromData(ba, "JPG")
        assert ok
        return pixmap

    # get the current page content
    def getCurrentPageScene(self):
        # get the current view and associated scene
        for child in self.tabs.currentWidget().children():
            if child.__class__.__name__ == "GraphicsView":
                # return the current scene
                return child.scene()

    def getCurrentPage(self):
        # get the current view and associated scene
        for child in self.tabs.currentWidget().children():
            if child.__class__.__name__ == "GraphicsView":
                return child

    # need to review
    def mousePressEvent(self, event):
        self._drawing = True
        self.last_point = event.pos()
        print("mouse press")
        # for child in self.tabs.currentWidget().children():
        #     if child.__class__.__name__ == "QGraphicsView":
        currentScene = self.getCurrentPageScene()
        items = currentScene.items()
        for item in items:
            if item.type().real == 10:
                stampItems = item.childItems()
                print("pos")
                print(item.x())
                print(item.y())

    # need to review
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.last_point = event.pos()
            print("mouse move and pressed")
            print(self.last_point)

    # need to review
    def mouseDoubleClickEvent(self, event):
        print("mouse move double clicked")
        self.getCurrentPageScene().editObject()

    # Delete selected objects
    # or edit object
    def keyPressEvent(self, event):
        # delete an object
        if event.key() == Qt.Key_Delete:
            qm = QMessageBox()
            ret = qm.question(self, '', _("Are you sure you want to delete those objects?"), qm.Yes | qm.No)

            if ret == qm.No:
                return
            self.getCurrentPageScene().removeItems()
        #edit an object
        elif event.key() == Qt.Key_E:
            self.getCurrentPageScene().editObject()

    # add a copyright to the page
    def newCopyRight(self):
        self.getCurrentPageScene().newCopyRight()

    def newCopyRightAllPages(self):
        print("newCopyRightAllPages")
        for x in range(0, self.tabs.count().real):
            print(x)
            self.tabs.setCurrentIndex(x)
            self.getCurrentPageScene().newCopyRight()

    def newImage(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Select picture", "", ("all pictures (*.jpg *.jpeg *.png);;PNG (*.png)" ),
                                                  options=options)
        self.getCurrentPageScene().addImage(fileName)

    def str_to_bool(self, s):
        if s == 'True':
            return True
        elif s == 'False':
            return False
        else:
            raise ValueError

    def configApp(self):
        print("config")
        dlg = ConfigDlg()
        res = dlg.exec_()

        if res == QDialog.Accepted:
            print("Clicked ok")

    # obsolete
    def showdialog(self):
        print("not used")

    # obsolete
    def testDialog(self):
        print("Dialog")
        info = "info"
        d = QDialog(self)
        l = QVBoxLayout()
        print("dialog 1")
        d.setLayout(l)
        v = QPlainTextEdit()
        d.setWindowTitle("title")
        v.setPlainText(info)
        v.setMinimumWidth(400)
        v.setMinimumHeight(350)
        l.addWidget(v)
        print("dialog 2-1")
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(d.accept)
        bb.rejected.connect(d.reject)
        l.addWidget(bb)
        print("dialog 2-2")
        bb.addButton('Copy to clipboard', bb.ActionRole)
        print("dialog 3")
        # bb.clicked.connect(lambda :
        #         #QApplication.clipboard().setText(v.toPlainText())
        #         #print("test")
        #         d.close()
        # )

        bb.clicked.connect(lambda:
                           self.saveStuff(d))
        res = d.exec_()
        if res == QDialog.Accepted:
            print("Clicked ok")
            print(v.toPlainText())
        if res == QDialog.Rejected:
            print("Clicked cancel")

    # obsolete
    def saveFile(self):
        # Logic for saving a file goes here...
        # export as xml form
        print("Export as xml")
        self.page.savePageToFile("albumfile.xml")

    # obsolete
    def openFile(self):
        # Logic for opening an existing file goes here...
        # self.centralWidget.setText("<b>File > Open...</b> clicked")
        print("Open page")

        self.page.openPage("albumfile.xml")

    # obsolete
    def saveStuff(self, dlg):
        print("in stuff")
        dlg.close()

