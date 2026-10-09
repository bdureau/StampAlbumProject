"""
Main Window Module
------------------
Contains the main application window ('Window') managing menus, toolbars,
tabbed page displays, actions, and file I/O operations (XML/gzip).

Author: Boris du Reau
"""
from ResizablePixmapItem import ResizablePixmapItem
from PageBorder import PageBorder
from AboutDlg import AboutDlg  # Import de la nouvelle boîte de dialogue
from PyQt6.QtCore import QPointF, Qt, QPoint, QByteArray, QRectF
from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtWidgets import (
    QMessageBox, QGraphicsPixmapItem,
    QGraphicsRectItem,
    QGraphicsScene, QFileDialog,
    QGraphicsView, QApplication, QLabel, QMainWindow, QMenuBar, QMenu,
    QToolBar,  QGraphicsTextItem, QGraphicsItemGroup, QDialog, QPushButton,
    QLineEdit, QFormLayout, QStatusBar, QTabWidget, QWidget, QVBoxLayout, QDialogButtonBox, QPlainTextEdit
)
from PyQt6.QtGui import QBrush, QPainter, QPen, QPixmap, QPolygonF, QImage, QIcon, QColor, QFont, QAction, QPageLayout
from PyQt6.QtPrintSupport import QPrintPreviewDialog, QPrinter, QPrintDialog
from Stamp import Stamp

from Page import Page
from ConfigDlg import ConfigDlg

import sys
import xml.etree.ElementTree as ET

from PageDlg import PageDlg

from GraphicsView import GraphicsView
import os, gzip
from TextDlg import TextDlg

import gettext
from PyQt6.QtGui import QAction, QIcon, QKeySequence

# Set up gettext localization
gettext.find("MainWindow")
translate = gettext.translation('MainWindow', localedir='locale', languages=['fr'])

translate.install()
_ = translate.gettext

FILE_FORMAT_VERSION = "1.0"

class Window(QMainWindow):
    """Main application window managing UI layout, actions, and user interactions."""

    def __init__(self, parent=None):
        """Initialize the main window and UI components."""
        super().__init__(parent)
        self.setWindowTitle("Stamp album")
        self.setWindowIcon(QtGui.QIcon('stamp_book1170.png'))

        # Set initial main window dimensions
        self.resize(int(222 / (25.4 / 96)), 800)

        # Track page count and recent stamp dialog selections
        self.pageCount = 0
        self.lastStampObj = {}
        self.lastStampObj['country'] = None
        self.lastStampObj['type'] = None
        self.lastStampObj['nbr'] = None
        self.lastStampObj['year'] = None


        # Central tab widget containing album pages
        self.tabs = QTabWidget()
        palette = self.tabs.palette()
        palette.setColor(self.tabs.backgroundRole(), Qt.GlobalColor.lightGray)
        self.tabs.setPalette(palette)
        self.tabs.resize(300, 200)

        # Create an initial default page
        self.newPage(None, True)
        self.setCentralWidget(self.tabs)

        self.currentAlbumName = ""

        # Initialize UI elements and action bindings
        self._createActions()
        self._createMenuBar()
        self._createToolBars()
        self._connectActions()

    def _createMenuBar(self):
        """Construct the main menu bar."""
        menuBar = self.menuBar()

        # File Menu
        fileMenu = QMenu(_("&File"), self)
        menuBar.addMenu(fileMenu)
        fileMenu.addAction(self.newAction)
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.saveAction)
        # print
        fileMenu.addAction(self.printAction)
        fileMenu.addAction(self.printPreviewCurrentPageAction)
        fileMenu.addAction(self.printPreviewAllPagesAction)
        fileMenu.addAction(self.printPDFAction)
        # exit
        fileMenu.addAction(self.exitAction)

        # Edit Menu
        editMenu = menuBar.addMenu(_("&Edit"))
        editMenu.addAction(self.undoAction)
        editMenu.addAction(self.redoAction)
        editMenu.addSeparator()
        editMenu.addAction(self.copyAction)
        editMenu.addAction(self.pasteAction)
        editMenu.addAction(self.cutAction)

        # Stamp Menu
        stampMenu = menuBar.addMenu(_("&Stamp"))
        stampMenu.addAction(self.newStampAction)
        stampMenu.addAction(self.editStampAction)

        # Alignment Menu
        alignMenu = menuBar.addMenu(_("Align"))
        alignMenu.addAction(self.alignLeftAction)
        alignMenu.addAction(self.alignRightAction)
        alignMenu.addAction(self.alignTopAction)
        alignMenu.addAction(self.alignBottomAction)
        alignMenu.addAction(self.centerHorizontallyAction)
        alignMenu.addAction(self.centerVerticallyAction)
        alignMenu.addAction(self.distributeVerticallyAction)
        alignMenu.addAction(self.distributeHorizontallyAction)

        # Page Menu
        pageMenu = menuBar.addMenu(_("Page"))
        pageMenu.addAction(self.newPageAction)
        pageMenu.addAction(self.deletePageAction)
        pageMenu.addAction(self.deletePageObjectsAction)
        pageMenu.addAction(self.drawGridAction)
        pageMenu.addAction(self.deleteAlbumAction)

        # Objects Menu
        objectMenu = menuBar.addMenu(_("Objects"))
        objectMenu.addAction(self.newTextAction)
        objectMenu.addAction(self.newRichTextAction)  # Add Rich Text to Objects menu
        objectMenu.addAction(self.newImageAction)
        objectMenu.addAction(self.newBorderAction)
        objectMenu.addAction(self.newCopyRightAction)
        objectMenu.addAction(self.newCopyRightAllPagesAction)
        objectMenu.addAction(self.newPageNbrAction)
        objectMenu.addAction(self.newPageNbrAllPagesAction)
        objectMenu.addAction(self.newYearToPageAction)
        objectMenu.addAction(self.newYearToAllPagesAction)

        # Config Menu
        configMenu = menuBar.addMenu(_("&Config"))
        configMenu.addAction(self.setupAppAction)

        # Help Menu
        helpMenu = menuBar.addMenu(_("&Help"))
        helpMenu.addAction(self.helpContentAction)
        helpMenu.addAction(self.aboutAction)

    def _createActions(self):
        """Define QAction instances for menus and toolbars."""
        # File Actions
        self.newAction = QAction(self)
        self.newAction.setText(_("&New"))
        iconNew = QIcon()
        iconNew.addPixmap(QPixmap("images/new.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.newAction.setIcon(iconNew)

        # Open
        self.openAction = QAction(_("&Open..."), self)
        iconOpen = QIcon()
        iconOpen.addPixmap(QPixmap("images/open.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.openAction.setIcon(iconOpen)
        self.openAction.setObjectName("actionOpen")

        # Save
        self.saveAction = QAction(_("&Save"), self)
        iconSave = QIcon()
        iconSave.addPixmap(QPixmap("images/save.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.saveAction.setIcon(iconSave)
        self.saveAction.setObjectName("actionSave")

        # print actions
        self.printAction = QAction(_("&Print all pages..."), self)
        iconPrint = QIcon()
        iconPrint.addPixmap(QPixmap("images/print.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.printAction.setIcon(iconPrint)
        self.printAction.setObjectName("printAction")

        # print preview
        self.printPreviewAllPagesAction = QAction(_("&Print preview all pages..."), self)
        iconPrintPreviewAllPages = QIcon()
        iconPrintPreviewAllPages.addPixmap(QPixmap("images/printprev.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.printPreviewAllPagesAction.setIcon(iconPrintPreviewAllPages)
        self.printPreviewAllPagesAction.setObjectName("printPreviewAllPagesAction")

        self.printPreviewCurrentPageAction = QAction(_("&Print preview current page..."), self)
        iconPrintPreviewCurrentPage = QIcon()
        iconPrintPreviewCurrentPage.addPixmap(QPixmap("images/printprev.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.printPreviewCurrentPageAction.setIcon(iconPrintPreviewCurrentPage)
        self.printPreviewCurrentPageAction.setObjectName("printPreviewCurrentPageAction")

        # print PDF
        self.printPDFAction = QAction(_("&Print current to PDF..."), self)
        iconPrintPDF = QIcon()
        iconPrintPDF.addPixmap(QPixmap("images/pdf.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.printPDFAction.setIcon(iconPrintPDF)
        self.printPDFAction.setObjectName("printPDFAction")

        # exit
        self.exitAction = QAction(_("&Exit"), self)
        iconExit = QIcon()
        iconExit.addPixmap(QPixmap("images/exit.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.exitAction.setIcon(iconExit)
        self.exitAction.setObjectName("exitAction")

        # Edit Actions
        self.copyAction = QAction(_("&Copy"), self)
        iconCopy = QIcon()
        iconCopy.addPixmap(QPixmap("images/copy.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.copyAction.setIcon(iconCopy)

        self.pasteAction = QAction(_("&Paste"), self)
        iconPaste = QIcon()
        iconPaste.addPixmap(QPixmap("images/paste.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.pasteAction.setIcon(iconPaste)


        self.cutAction = QAction(_("C&ut"), self)
        iconCut = QIcon()
        iconCut.addPixmap(QPixmap("images/cut.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.cutAction.setIcon(iconCut)

        # Stamp Actions
        self.newStampAction = QAction(_("New Stamp ..."), self)
        self.editStampAction = QAction(_("Edit Current Stamp ..."), self)
        stampIcon = QIcon()
        stampIcon.addPixmap(QPixmap("images/stamp.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.newStampAction.setIcon(stampIcon)


        # Page Actions
        self.newPageAction = QAction(_("New Page ..."), self)
        iconNewPage = QIcon()
        iconNewPage.addPixmap(QPixmap("images/page.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.newPageAction.setIcon(iconNewPage)

        self.deletePageAction = QAction(_("Delete Page ..."), self)
        iconDeletePage = QIcon()
        iconDeletePage.addPixmap(QPixmap("images/delete_page.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.deletePageAction.setIcon(iconDeletePage)

        self.deletePageObjectsAction = QAction(_("Delete Page Objects..."), self)

        iconDeletePageObjects = QIcon()
        iconDeletePageObjects.addPixmap(QPixmap("images/clear_page.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.deletePageObjectsAction.setIcon(iconDeletePageObjects)

        self.drawGridAction = QAction(_("Grid on/off"), self)
        iconDrawGrid = QIcon()
        iconDrawGrid.addPixmap(QPixmap("images/grid.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.drawGridAction.setIcon(iconDrawGrid)

        self.deleteAlbumAction = QAction(_("Delete Album ..."), self)
        iconDelete = QIcon()
        iconDelete.addPixmap(QPixmap("images/trash.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.deleteAlbumAction.setIcon(iconDelete)


        # Object Actions
        self.newTextAction = QAction(_("New text ..."), self)
        iconNewText = QIcon()
        iconNewText.addPixmap(QPixmap("images/text.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.newTextAction.setIcon(iconNewText)

        # Action for Rich Text
        self.newRichTextAction = QAction(_("New Rich Text ..."), self)
        iconRichText = QIcon()
        iconRichText.addPixmap(QPixmap("images/text.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.newRichTextAction.setIcon(iconRichText)

        self.newImageAction = QAction(_("New Image ..."), self)
        iconNewImage = QIcon()
        iconNewImage.addPixmap(QPixmap("images/image.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.newImageAction.setIcon(iconNewImage)

        self.newCopyRightAction = QAction(_("New copyright"), self)
        iconCopyright = QIcon()
        iconCopyright.addPixmap(QPixmap("images/copyright.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.newCopyRightAction.setIcon(iconCopyright)

        self.newCopyRightAllPagesAction = QAction(_("New copyright all pages"), self)
        iconCopyrightAllPages = QIcon()
        iconCopyrightAllPages.addPixmap(QPixmap("images/page_copyright.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.newCopyRightAllPagesAction.setIcon(iconCopyrightAllPages)

        self.newBorderAction = QAction(_("New Page border"), self)
        iconNewBorder = QIcon()
        iconNewBorder.addPixmap(QPixmap("images/border.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.newBorderAction.setIcon(iconNewBorder)

        self.newPageNbrAction = QAction(_("New page nbr"), self)
        iconPageNbr = QIcon()
        iconPageNbr.addPixmap(QPixmap("images/number.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.newPageNbrAction.setIcon(iconPageNbr)

        self.newPageNbrAllPagesAction = QAction(_("New page nbr all pages"), self)
        iconPageNbrAllPages = QIcon()
        iconPageNbrAllPages.addPixmap(QPixmap("images/number.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.newPageNbrAllPagesAction.setIcon(iconPageNbrAllPages)

        self.newYearToPageAction = QAction(_("Add year to page"), self)
        iconAddYear = QIcon()
        iconAddYear.addPixmap(QPixmap("images/add_year.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.newYearToPageAction.setIcon(iconAddYear)

        self.newYearToAllPagesAction = QAction(_("Add year to all pages"), self)

        # Alignment Actions
        self.alignLeftAction = QAction(_("Align Left"), self)
        iconAlignLeft = QIcon()
        iconAlignLeft.addPixmap(QPixmap("images/align_left.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.alignLeftAction.setIcon(iconAlignLeft)

        self.alignRightAction = QAction(_("Align Right"), self)
        iconAlignRight = QIcon()
        iconAlignRight.addPixmap(QPixmap("images/align_right.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.alignRightAction.setIcon(iconAlignRight)

        self.alignTopAction = QAction(_("Align Top"), self)
        iconAlignTop = QIcon()
        iconAlignTop.addPixmap(QPixmap("images/align_top.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.alignTopAction.setIcon(iconAlignTop)

        self.alignBottomAction = QAction(_("Align Bottom"), self)
        iconAlignBottom = QIcon()
        iconAlignBottom.addPixmap(QPixmap("images/align_bottom.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.alignBottomAction.setIcon(iconAlignBottom)

        self.distributeVerticallyAction = QAction(_("Distribute Vertically"), self)
        iconDistributeVertically = QIcon()
        iconDistributeVertically.addPixmap(QPixmap("images/distribute_vertical.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.distributeVerticallyAction.setIcon(iconDistributeVertically)

        self.distributeHorizontallyAction = QAction(_("Distribute Horizontally"), self)
        iconDistributeHorizontally = QIcon()
        iconDistributeHorizontally.addPixmap(QPixmap("images/distribute_horiz.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.distributeHorizontallyAction.setIcon(iconDistributeHorizontally)

        self.centerHorizontallyAction = QAction(_("Center Horizontally"), self)
        iconCenterHorizontally = QIcon()
        iconCenterHorizontally.addPixmap(QPixmap("images/center_horizontal.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.centerHorizontallyAction.setIcon(iconCenterHorizontally)

        self.centerVerticallyAction = QAction(_("Center Vertically"), self)
        iconCenterVertically = QIcon()
        iconCenterVertically.addPixmap(QPixmap("images/center_vertical.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.centerVerticallyAction.setIcon(iconCenterVertically)

        # Config & Help Actions
        self.setupAppAction = QAction(_("Setup application"), self)
        iconSetup = QIcon()
        iconSetup.addPixmap(QPixmap("images/config.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.setupAppAction.setIcon(iconSetup)

        self.helpContentAction = QAction(_("&Help Content"), self)
        iconHelp = QIcon()
        iconHelp.addPixmap(QPixmap("images/help.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.helpContentAction.setIcon(iconHelp)

        self.aboutAction = QAction(_("&About"), self)
        iconAbout = QIcon()
        iconAbout.addPixmap(QPixmap("images/about.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.aboutAction.setIcon(iconAbout)

        # Action Annuler (Ctrl+Z)
        self.undoAction = QAction(_("&Undo"), self)
        self.undoAction.setShortcut(QKeySequence.StandardKey.Undo)
        self.undoAction.setIcon(QIcon("images/undo.png"))  # ou via qtawesome
        self.undoAction.triggered.connect(self.undo)

        # Action Rétablir (Ctrl+Y / Shift+Ctrl+Z)
        self.redoAction = QAction(_("&Redo"), self)
        self.redoAction.setShortcut(QKeySequence.StandardKey.Redo)
        self.redoAction.setIcon(QIcon("images/redo.png"))
        self.redoAction.triggered.connect(self.redo)

    def _createToolBars(self):
        """Construct application toolbars."""
        # File Toolbar
        fileToolBar = self.addToolBar("File")
        fileToolBar.addAction(self.newAction)
        fileToolBar.addAction(self.openAction)
        fileToolBar.addAction(self.saveAction)
        fileToolBar.addAction(self.printPDFAction)
        fileToolBar.addAction(self.printPreviewAllPagesAction)
        fileToolBar.addAction(self.printPreviewCurrentPageAction)
        fileToolBar.addAction(self.exitAction)

        # Edit Toolbar
        editToolBar = QToolBar("Edit", self)
        editToolBar.addAction(self.copyAction)
        editToolBar.addAction(self.pasteAction)
        editToolBar.addAction(self.cutAction)
        self.addToolBar(editToolBar)

        # Page Toolbar
        pageToolBar = QToolBar("Page", self)
        pageToolBar.addAction(self.newPageAction)
        pageToolBar.addAction(self.deletePageAction)
        pageToolBar.addAction(self.deletePageObjectsAction)
        pageToolBar.addAction(self.drawGridAction)
        pageToolBar.addAction(self.deleteAlbumAction)
        self.addToolBar(pageToolBar)

        # Alignment Toolbar
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

        # Stamp Toolbar
        stampToolBar = QToolBar("Stamp", self)
        stampToolBar.addAction(self.newStampAction)
        self.addToolBar(stampToolBar)

        # Objects Toolbar
        objectToolBar = QToolBar("Objects", self)
        objectToolBar.addAction(self.newTextAction)
        objectToolBar.addAction(self.newRichTextAction)  # Add Rich Text button to toolbar
        self.addToolBar(objectToolBar)

        # Help Toolbar
        helpToolBar = QToolBar("Help", self)
        helpToolBar.addAction(self.helpContentAction)
        helpToolBar.addAction(self.aboutAction)
        helpToolBar.addAction(self.setupAppAction)
        self.addToolBar(helpToolBar)

        # Status Bar
        statusBar = QStatusBar(self)
        statusBar.setObjectName("statusBar")
        self.setStatusBar(statusBar)

    def _connectActions(self):
        """Connect UI actions to their respective handler functions."""
        # File signals
        self.newAction.triggered.connect(self.newFile)
        self.openAction.triggered.connect(self.openAlbumFile)
        self.saveAction.triggered.connect(self.saveAlbumToFile)
        self.printAction.triggered.connect(self.printAllPagesPDF)
        self.printPDFAction.triggered.connect(self.printPagePDF)
        self.printPreviewAllPagesAction.triggered.connect(self.printPreviewAllPages)
        self.printPreviewCurrentPageAction.triggered.connect(self.printPreviewCurrentPage)
        self.exitAction.triggered.connect(self.exitApp)

        # Edit signals
        self.copyAction.triggered.connect(self.copy)
        self.cutAction.triggered.connect(self.cut)
        self.pasteAction.triggered.connect(self.paste)

        # Alignment signals
        self.alignBottomAction.triggered.connect(self.alignBottom)
        self.alignTopAction.triggered.connect(self.alignTop)
        self.alignLeftAction.triggered.connect(self.alignLeft)
        self.alignRightAction.triggered.connect(self.alignRight)
        self.distributeHorizontallyAction.triggered.connect(self.distributeHorizontally)
        self.distributeVerticallyAction.triggered.connect(self.distributeVertically)
        self.centerVerticallyAction.triggered.connect(self.centerVertically)
        self.centerHorizontallyAction.triggered.connect(self.centerHorizontally)

        # Config signal
        self.setupAppAction.triggered.connect(self.configApp)

        # Stamp signals
        self.newStampAction.triggered.connect(self.createNewStamp)
        self.editStampAction.triggered.connect(self.editStamp)

        # Page signals
        self.newPageAction.triggered.connect(self.newPage)
        self.deletePageAction.triggered.connect(self.deleteCurrentPage)
        self.deletePageObjectsAction.triggered.connect(self.clearPageObjects)
        self.drawGridAction.triggered.connect(self.gridOnOff)
        self.deleteAlbumAction.triggered.connect(self.deleteAlbum)

        # Object signals
        self.newTextAction.triggered.connect(self.createText)
        self.newRichTextAction.triggered.connect(self.createRichText)  # Connect to handler
        self.newCopyRightAction.triggered.connect(self.newCopyRight)
        self.newCopyRightAllPagesAction.triggered.connect(self.newCopyRightAllPages)
        self.newImageAction.triggered.connect(self.newImage)
        self.newBorderAction.triggered.connect(self.newBorder)
        self.newPageNbrAction.triggered.connect(self.newPageNbr)
        self.newPageNbrAllPagesAction.triggered.connect(self.newPageNbrAllPages)
        self.newYearToPageAction.triggered.connect(self.addYearToPage)
        self.newYearToAllPagesAction.triggered.connect(self.addYearToAllPages)

        # Help signals
        self.aboutAction.triggered.connect(self.about)
        self.helpContentAction.triggered.connect(self.help)

    def closeEvent(self, event):
        """Prompt user confirmation before closing the application window."""
        print("User has clicked the red x on the main window")
        qm = QMessageBox()
        ret = qm.question(self, _('Exit'), _("Are you sure you want to exit the application?"),
                          qm.StandardButton.Yes | qm.StandardButton.No)

        if ret == qm.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

    def undo(self):
        """Annule la dernière action sur la page active."""
        scene = self.getCurrentPageScene()
        if scene and hasattr(scene, "undoStack"):
            scene.undoStack.undo()

    def redo(self):
        """Rétablit la dernière action annulée sur la page active."""
        scene = self.getCurrentPageScene()
        if scene and hasattr(scene, "undoStack"):
            scene.undoStack.redo()

    def exitApp(self):
        """Close the main window."""
        print("exit app")
        self.close()

    def newPage(self, _pageType=None, border=None):
        """Create and append a new album page tab."""
        if _pageType is not None and (_pageType == 'portrait' or _pageType == 'landscape'):
            self.pageType = _pageType
        else:
            self.pageType = "portrait"
            pDlg = PageDlg()
            res = pDlg.exec()

            #accepted
            if res == 1:
                if pDlg.pageType == "portrait":
                    print("portrait")
                    self.pageType = "portrait"
                    border = True
                else:
                    print("landscape")
                    self.pageType = "landscape"
                    border = True
            #rejected
            if res == 0:
                return

        page = Page(self.pageType, border)
        view = GraphicsView(page)
        view.scrollContentsBy(0, 0)

        tab1 = QWidget()
        tab1.layout = QVBoxLayout(self)
        tab1.layout.addWidget(view)
        tab1.setLayout(tab1.layout)
        tab1.setAutoFillBackground(True)

        palette = tab1.palette()
        palette.setColor(tab1.backgroundRole(), Qt.GlobalColor.lightGray)
        tab1.setPalette(palette)

        self.pageCount = self.pageCount + 1
        currentPage = self.tabs.insertTab(self.tabs.currentIndex()+1, tab1, "Page " + str(self.tabs.count().real))

        # Update tab labels in sequence
        for x in range(0, self.tabs.count().real):
            self.tabs.setCurrentIndex(x)
            self.tabs.setTabText(self.tabs.currentIndex(), "Page " + str(x+1))

        self.tabs.setCurrentIndex(currentPage)
        return page

    # clear objects on current page
    def clearPageObjects(self):
        """Clear all graphic items on the current active page."""
        print("clear page")
        qm = QMessageBox()
        ret = qm.question(self, _('Delete all objects'), _("Are you sure you want clear the current page?"),
                          qm.StandardButton.Yes | qm.StandardButton.No)

        if ret == qm.StandardButton.Yes:
            self.getCurrentPageScene().clearPage()

    def deleteCurrentPage(self):
        """Remove the active page tab from the album."""
        qm = QMessageBox()
        ret = qm.question(self, _('Delete current page'), _("Are you sure you want to delete the current page?"),
                          qm.StandardButton.Yes | qm.StandardButton.No)

        if ret == qm.StandardButton.No:
            return
        # only allow delete if number of page is greater than one
        if self.tabs.count().real > 0:
            self.tabs.removeTab(self.tabs.currentIndex())

            for x in range(0, self.tabs.count().real):
                self.tabs.setCurrentIndex(x)
                self.tabs.setTabText(self.tabs.currentIndex(), "Page " + str(x + 1))

    def deleteAllPages(self):
        """Remove all pages from the tab widget."""
        print("Delete all pages")
        for x in range(self.tabs.count()):
            self.tabs.removeTab(self.tabs.currentIndex())
        self.pageCount = 0

        self.currentAlbumName = ""

    # delete entire album
    def deleteAlbum(self):
        """Delete the entire album and reset state."""
        print("delete current album")
        qm = QMessageBox()
        ret = qm.question(self, _('Delete album'), _("Are you sure you want to delete the entire album?"),
                          qm.StandardButton.Yes | qm.StandardButton.No)

        if ret == qm.StandardButton.No:
            return
        self.deleteAllPages()
        self.currentAlbumName = ""

    def newBorder(self):
        """Add a new page border using the default style configured in settings."""
        scene = self.getCurrentPageScene()
        if scene.pageType == "portrait":
            scene.addBorder(
                177 / (25.4 / 96.0),
                272 / (25.4 / 96.0),
                19 / (25.4 / 96.0),
                0, 0, 0
            )
        else:
            scene.addBorder(
                272 / (25.4 / 96.0),
                177 / (25.4 / 96.0),
                ((297 - 272) / 2) / (25.4 / 96.0),
                0, 19 / (25.4 / 96.0), 0
            )

    # file menu functions
    def newFile(self):
        """Clear existing pages and start a fresh album file."""
        print("creating new File")
        # Ask user about confirmation on deleting all pages
        qm = QMessageBox()
        ret = qm.question(self, _('Delete all pages'), _("Are you sure you want to delete all the pages?"),
                          qm.StandardButton.Yes | qm.StandardButton.No)

        if ret == qm.StandardButton.No:
            return
        # Delete all pages
        self.deleteAllPages()
        # Create one empty page
        self.newPage(None, True)

    def createRichText(self):
        """Create a new rich text block on the current active page."""
        scene = self.getCurrentPageScene()
        if scene and hasattr(scene, "addRichText"):
            scene.addRichText()

    def newPageNbr(self):
        """Add a page number to the current page."""
        #print("newPageNbr")
        self.getCurrentPageScene().newPageNbr()

    def newPageNbrAllPages(self):
        """Prompt user and apply page numbers across all album pages."""
        textLabel = QGraphicsTextItem("")
        textLabelFont = textLabel.font()
        textLabelFont.setPointSize(8)
        textLabel.setFont(textLabelFont)

        dlg = TextDlg(textLabel)
        res = dlg.exec()
        #accepted
        if res == 1:
            text = dlg.eTXT.toPlainText()
            font = dlg.eTXT.font()
            align = dlg.eTXT.alignment()

            for x in range(0, self.tabs.count().real):
                self.tabs.setCurrentIndex(x)
                self.getCurrentPageScene().addPageNbr(text + " " + str(self.tabs.currentIndex() + 1), font, align)

        #rejected
        if res == 0:
            print("Clicked cancel")

    def addYearToPage(self):
        """Add a year header to the active page."""
        self.getCurrentPageScene().addPageYear()

    def addYearToAllPages(self):
        """Prompt user and apply a year header across all album pages."""
        textLabel = QGraphicsTextItem("")
        textLabelFont = textLabel.font()
        textLabelFont.setPointSize(10)
        textLabelFont.setBold(True)
        textLabel.setFont(textLabelFont)

        dlg = TextDlg(textLabel)
        res = dlg.exec()
        #accepted
        if res == 1:
            text = dlg.eTXT.toPlainText()
            font = dlg.eTXT.font()
            align = dlg.eTXT.alignment()

            for x in range(0, self.tabs.count().real):
                self.tabs.setCurrentIndex(x)
                self.getCurrentPageScene().addYear(text, font, align)

        #rejected
        if res == 0:
            print("Clicked cancel")

    def openAlbumFile(self):
        """Open and deserialize a compressed (.sta) album XML file."""
        qm = QMessageBox()
        ret = qm.question(
            self, "Delete all pages", "Are you sure you want to delete all the pages?",
            qm.StandardButton.Yes | qm.StandardButton.No
        )

        if ret == qm.StandardButton.No:
            return

        self.deleteAllPages()
        options = QFileDialog.Option.DontUseNativeDialog

        fileName, _ = QFileDialog.getOpenFileName(
            self, "Open Album file", "", "Album Files (*.sta)", options=options
        )
        if not fileName:
            return

        fileNameArray = fileName.split(".")
        if fileNameArray[len(fileNameArray) - 1] == "sta":
            f = gzip.open(fileName, 'r')
        else:
            f = open(fileName, 'r')

        self.currentAlbumName = fileName
        mytree = ET.parse(f)
        f.close()
        myroot = mytree.getroot()

        file_version = myroot.attrib.get("version", "0.9")
        print(f"Loading album file format version: {file_version}")

        for it in myroot.findall('page'):
            self.newPage(str(it.attrib.get("type")), False)
            currentPage = self.getCurrentPageScene()

            # --- Restore Standard Text Labels ---
            textLabelsItems = it.findall('textLabel')
            for textLabel in textLabelsItems:
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

            # --- Restore Rich Text Labels ---
            richTextLabelsItems = it.findall('richTextLabel')
            for richLabel in richTextLabelsItems:
                html_element = richLabel.find('html_label')
                html_content = html_element.text if html_element is not None else ""

                pos = richLabel.find('labelPos')
                x = pos.find('x').text if pos is not None and pos.find('x') is not None else 50.0
                y = pos.find('y').text if pos is not None and pos.find('y') is not None else 50.0

                currentPage.addRichText(html_content, float(x), float(y))

            # --- Restore Standalone Images ---
            imageItems = it.findall('imageItem')
            for img_node in imageItems:
                pixmap_data = img_node.find('pixmapData')
                if pixmap_data is not None and pixmap_data.text:
                    pixmap = self.bytesToPixmap(pixmap_data.text)

                    if not pixmap.isNull():
                        pos = img_node.find('imagePos')
                        x = float(pos.find('x').text) if pos is not None and pos.find('x') is not None else 50.0
                        y = float(pos.find('y').text) if pos is not None and pos.find('y') is not None else 50.0
                        scale_val = float(img_node.find('scale').text) if img_node.find('scale') is not None else 1.0

                        # Re-create ResizablePixmapItem with stored position and scale
                        pixmap_item = ResizablePixmapItem(pixmap)
                        pixmap_item.setPos(x, y)
                        pixmap_item.setScale(scale_val)

                        currentPage.addItem(pixmap_item)

            # --- Restore Copyright Labels ---
            copyrightLabelsItems = it.findall('labelCopyRight')
            for copyrightLabel in copyrightLabelsItems:
                label = copyrightLabel.find('label').text
                font = copyrightLabel.find('font')
                myFont = QFont()
                myFont.setBold(self.str_to_bool(font.find('bold').text))
                myFont.setUnderline(self.str_to_bool(font.find('underline').text))
                myFont.setItalic(self.str_to_bool(font.find('italic').text))
                myFont.setStrikeOut(self.str_to_bool(font.find('strikeOut').text))
                myFont.setPointSize(int(font.find('pointSize').text))

                pos = copyrightLabel.find('labelPos')
                currentPage.addTextLabel(
                    label, float(pos.find('x').text), float(pos.find('y').text),
                    myFont, Qt.AlignmentFlag.AlignLeft, "labelCopyRight"
                )

            # --- Restore Page Number Labels ---
            pageNbrLabelsItems = it.findall('labelPageNbr')
            for pageNbrLabel in pageNbrLabelsItems:
                label = pageNbrLabel.find('label').text
                font = pageNbrLabel.find('font')
                myFont = QFont()
                myFont.setBold(self.str_to_bool(font.find('bold').text))
                myFont.setUnderline(self.str_to_bool(font.find('underline').text))
                myFont.setItalic(self.str_to_bool(font.find('italic').text))
                myFont.setStrikeOut(self.str_to_bool(font.find('strikeOut').text))
                myFont.setPointSize(int(font.find('pointSize').text))

                pos = pageNbrLabel.find('labelPos')
                currentPage.addTextLabel(
                    label, float(pos.find('x').text), float(pos.find('y').text),
                    myFont, Qt.AlignmentFlag.AlignLeft, "labelPageNbr"
                )

            # --- Restore Year Labels ---
            yearLabelsItems = it.findall('labelYear')
            for yearLabel in yearLabelsItems:
                label = yearLabel.find('label').text
                font = yearLabel.find('font')
                myFont = QFont()
                myFont.setBold(self.str_to_bool(font.find('bold').text))
                myFont.setUnderline(self.str_to_bool(font.find('underline').text))
                myFont.setItalic(self.str_to_bool(font.find('italic').text))
                myFont.setStrikeOut(self.str_to_bool(font.find('strikeOut').text))
                myFont.setPointSize(int(font.find('pointSize').text))

                pos = yearLabel.find('labelPos')
                currentPage.addTextLabel(
                    label, float(pos.find('x').text), float(pos.find('y').text),
                    myFont, Qt.AlignmentFlag.AlignCenter, "labelYear"
                )

            # --- Restore Page Borders ---
            pageBorderItem = it.findall('borderGroup')
            for border in pageBorderItem:
                pos = border.find('borderPos')
                x = pos.find('x').text
                y = pos.find('y').text
                width1 = border.find('width1').text
                height1 = border.find('height1').text
                border_style = border.attrib.get("style", PageBorder.STYLE_TRIPLE)

                currentPage.addBorder(
                    float(width1), float(height1),
                    float(x), float(y), 0, 0, style=border_style
                )

            # --- Restore Stamp Groups ---
            stampItems = it.findall('stampGroup')
            for stamp in stampItems:
                pos = stamp.find('stampPos')
                x = pos.find('x').text
                y = pos.find('y').text

                sizeBox = stamp.find('stampBox')
                width = sizeBox.find('width').text
                height = sizeBox.find('height').text
                try:
                    stampBox_width = sizeBox.find('stampBox_width').text
                    stampBox_height = sizeBox.find('stampBox_height').text
                    use_new = 1
                except:
                    use_new = 0

                stampDesc = stamp.find('stampDesc').text or ""
                stampNbr = stamp.find('stampNbr').text
                stampValue = stamp.find('stampValue').text
                pixmapItem = stamp.find('pixmapItem').text

                stamp_obj = Stamp()
                pixmap = self.bytesToPixmap(pixmapItem)

                if use_new == 1:
                    stamp_obj.createStampPix(
                        currentPage, str(stampNbr), str(stampValue), str(stampDesc),
                        float(stampBox_width), float(stampBox_height),
                        float(x), float(y), pixmap
                    )
                else:
                    stamp_obj.createStampPix(
                        currentPage, str(stampNbr), str(stampValue), str(stampDesc),
                        float(width) * (25.4 / 96.0), float(height) * (25.4 / 96.0),
                        float(x), float(y), pixmap
                    )

    # save an album to a file
    def saveAlbumToFile(self):
        """Serialize album structure into a gzip-compressed XML file (.sta)."""
        options = QFileDialog.Option.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(
            self, "Save Album", "", "Album Files (*.sta)", options=options
        )
        if fileName:
            if fileName.find(".") != -1:
                fileNameArray = fileName.split(".")
                if fileNameArray[len(fileNameArray) - 1] == "sta":
                    fileName = fileName.rsplit('.', maxsplit=1)[0]
        else:
            return

        self.currentAlbumName = fileName
        # Set file format version on root element
        root = ET.Element("album", version=FILE_FORMAT_VERSION)

        for x in range(self.tabs.count()):
            self.tabs.setCurrentIndex(x)

            currentScene = self.getCurrentPageScene()
            page = ET.SubElement(
                root, "page", name="%s" % x, type="%s" % currentScene.pageType
            )
            items = currentScene.items()

            for item in items:
                # 1. Text Items (QGraphicsTextItem)
                if item.type().real == 8:
                    par = item.parentItem()
                    if par is None:
                        item_type = item.data(0) or "textLabel"
                        textLbl = ET.SubElement(page, item_type)

                        if item_type == "richTextLabel":
                            # Save complete HTML structure for rich text items
                            ET.SubElement(textLbl, "html_label").text = item.toHtml()
                        else:
                            # Standard plaintext label serialization
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

                # 2. Standalone Image Items (QGraphicsPixmapItem / ResizablePixmapItem)
                elif item.type().real == 7:
                    par = item.parentItem()
                    if par is None:
                        img_node = ET.SubElement(page, "imageItem")

                        # Serialize pixmap to Base64 PNG string
                        pix = item.pixmap()
                        ET.SubElement(img_node, "pixmapData").text = str(self.pixmapToBytes(pix))

                        # Save position and scale factor
                        pos = ET.SubElement(img_node, "imagePos")
                        ET.SubElement(pos, "x").text = str(item.x())
                        ET.SubElement(pos, "y").text = str(item.y())
                        ET.SubElement(img_node, "scale").text = str(item.scale())

                # 3. Page Border Group
                elif item.type().real == 10 and item.data(0) == "borderGroup":
                    border = ET.SubElement(page, item.data(0))
                    border_style = item.data(4) or PageBorder.STYLE_TRIPLE
                    border.set("style", str(border_style))

                    borderItems = item.childItems()
                    pos = ET.SubElement(border, "borderPos")
                    ET.SubElement(pos, "x").text = str(item.x())
                    ET.SubElement(pos, "y").text = str(item.y())
                    i = 0
                    for borderItem in borderItems:
                        if borderItem.type().real == 3:
                            i += 1
                            ET.SubElement(border, "width" + str(i)).text = str(borderItem.data(1))
                            ET.SubElement(border, "height" + str(i)).text = str(borderItem.data(2))

                # 4. Stamp Group Item
                elif item.type().real == 10 and item.data(0) == "stampGroup":
                    stamp = ET.SubElement(page, item.data(0))
                    stampItems = item.childItems()

                    pos = ET.SubElement(stamp, "stampPos")
                    ET.SubElement(pos, "x").text = str(item.x())
                    ET.SubElement(pos, "y").text = str(item.y())
                    for stampItem in stampItems:
                        if stampItem.type().real == 8:
                            ET.SubElement(stamp, stampItem.data(0)).text = stampItem.toPlainText()
                        elif stampItem.type().real == 7:
                            pix = stampItem.pixmap()
                            ET.SubElement(stamp, stampItem.data(0)).text = str(self.pixmapToBytes(pix))
                        elif stampItem.type().real == 3:
                            size = ET.SubElement(stamp, stampItem.data(0))
                            ET.SubElement(size, "width").text = str(stampItem.boundingRect().width())
                            ET.SubElement(size, "height").text = str(stampItem.boundingRect().height())
                            ET.SubElement(size, "stampBox_width").text = str(int(stampItem.data(1)))
                            ET.SubElement(size, "stampBox_height").text = str(int(stampItem.data(2)))

        tree = ET.ElementTree(root)
        tree.write(fileName)

        # Compress XML to Gzip file (.sta)
        f = gzip.open(fileName + '.sta', 'wb')
        ET.ElementTree(root).write(f)
        f.close()

        # Remove temporary uncompressed XML file
        if os.path.isfile(fileName):
            os.remove(fileName)

    # print all pages
    def printAllPagesPDF(self):
        """Export all album pages into a single PDF document."""
        print("print all pages")
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        #printer.setPageSize(QtGui.QPagedPaintDevice.A4)

        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)

        printer.setOutputFileName(self.currentAlbumName + ".pdf")
        scale = printer.resolution() / 96.0

        printer.setPageMargins(QtCore.QMarginsF(0.0, 0.0, 0.0, 0.0), QtGui.QPageLayout.Unit.Millimeter)
        p = QPainter(printer)
        for x in range(self.tabs.count()):
            self.tabs.setCurrentIndex(x)
            currentScene = self.getCurrentPageScene()

            # first unselect all objects
            for item in currentScene.items():
                item.setSelected(False)

            if currentScene.pageType == "portrait":
                printer.setPageOrientation(QPageLayout.Orientation.Portrait)
                print("Portrait")
            else:
                printer.setPageOrientation(QPageLayout.Orientation.Landscape)
                print("Landscape")
            if x > 0:
                printer.newPage()

            source = QtCore.QRectF(0, 0, currentScene.width(), currentScene.height())
            target = QRectF(0, 0, source.size().width() * scale, source.size().height() * scale)

            currentScene.render(p, target, source)

        p.end()

    # print all pages
    def printPreviewAllPages(self):
        """Open print preview dialog for all pages."""
        print("printPreviewAllPages")
        previewDialog = QPrintPreviewDialog()
        previewDialog.printer().setResolution(QPrinter.PrinterMode.HighResolution.value)
        previewDialog.printer().setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        #previewDialog.printer().setPageSize(QtGui.QPagedPaintDevice.A4)
        previewDialog.paintRequested.connect(self.createPreview)
        previewDialog.exec()

    def createPreview(self, printer):
        """Paint target pages into the QPrintPreviewDialog context."""
        scale = printer.resolution() / 96.0
        printer.setPageMargins(QtCore.QMarginsF(0.0, 0.0, 0.0, 0.0), QtGui.QPageLayout.Unit.Millimeter)

        p = QPainter(printer)
        for x in range(self.tabs.count()):
            self.tabs.setCurrentIndex(x)

            currentScene = self.getCurrentPageScene()

            if currentScene.pageType == "portrait":
                printer.setPageOrientation(QPageLayout.Orientation.Portrait)
            else:
                printer.setPageOrientation(QPageLayout.Orientation.Landscape)

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
        """Export active page to a PDF file."""
        print("print to PDF")
        options = QFileDialog.Option.DontUseNativeDialog
        fileName2, _ = QFileDialog.getSaveFileName(self, "Save current page", "album.pdf",
                                                   "(*.pdf)", options=options)
        if fileName2:
            print(fileName2)
        else:
            return
        self.getCurrentPageScene().printPagePDF(fileName2)

    # print preview the current page
    def printPreviewCurrentPage(self):
        """Display print preview for the active page."""
        print("Print preview page")
        self.getCurrentPageScene().printPreview()

    # need to be written !!!
    def importFileFromExcel(self):
        print("import file from Excel")

    # edit menu functions
    # copy selected object(s)
    def copy(self):
        """Copy selected scene items to clipboard."""
        self.getCurrentPage().copy_items()

    def cut(self):
        """Cut selected scene items to clipboard."""
        self.getCurrentPage().copy_items()
        self.getCurrentPageScene().removeItems()

    # paste objects that have been copied or cut to the current page
    def paste(self):
        """Paste scene items from clipboard."""
        self.getCurrentPage().paste_items()

    # stamp menu functions
    def createNewStamp(self):
        """Open creation dialog to insert a new stamp item."""
        stamp = self.getCurrentPageScene().newStamp(self.lastStampObj)
        if stamp is not None:
            self.lastStampObj['year'] = stamp['year']
            self.lastStampObj['type'] = stamp['type']
            self.lastStampObj['country'] = stamp['country']
            self.lastStampObj['nbr'] = stamp['nbr']

    # edit current selected stamp
    def editStamp(self):
        """Edit currently selected stamp item."""
        self.getCurrentPageScene().editObject()

    def about(self):
        """Display custom scrollable 'About' dialog."""
        dlg = AboutDlg(self)
        dlg.exec()
    # application on line help
    def help(self):
        """Open user help PDF document in default system viewer."""
        if sys.platform.startswith('win32'):
            os.startfile("Help\\StampAlbum Manuel utilisateur 03-11-2024.pdf")

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
        """Create a new floating text label."""
        print("create text")
        self.getCurrentPageScene().newLabel()

    # turn the grid on and off
    def gridOnOff(self):
        """Toggle grid pattern background in active scene."""
        child = self.getCurrentPageScene()
        if child.gridOn:
            child.setBackgroundBrush(QBrush(self.deleteGrid()))
            child.gridOn = False
        else:
            child.setBackgroundBrush(QBrush(self.drawGrid()))
            child.gridOn = True

    # used to draw the grid
    def drawGrid(self):
        """Generate grid texture pixmap."""
        self.pixmap = QPixmap(10, 10)
        pixmapWidth = self.pixmap.width() - 1
        painter = QPainter()

        self.pixmap.fill(Qt.GlobalColor.transparent)

        painter.begin(self.pixmap)
        painter.setPen(Qt.GlobalColor.gray)
        painter.drawLine(0, 0, pixmapWidth, 0)
        painter.drawLine(0, 0, 0, pixmapWidth)
        painter.end()
        return self.pixmap

    def deleteGrid(self):
        """Generate transparent texture pixmap to disable grid."""
        pixmap = QPixmap(10, 10)
        pixmap.fill(Qt.GlobalColor.transparent)
        return pixmap

    def pixmapToBytes(self, pixmap):
        """Encode QPixmap to Base64 PNG string."""
        ba = QtCore.QByteArray()
        buff = QtCore.QBuffer(ba)
        buff.open(QtCore.QIODevice.OpenModeFlag.WriteOnly)
        ok = pixmap.save(buff, "PNG")
        assert ok
        return bytes(ba.toBase64()).decode()

    def bytesToPixmap(self, pixmap_bytes):
        """Decode Base64 PNG string back to QPixmap."""
        ba = QtCore.QByteArray().fromBase64(pixmap_bytes.encode())
        pixmap = QtGui.QPixmap()
        ok = pixmap.loadFromData(ba, "PNG")
        assert ok
        return pixmap


    # get the current page content
    def getCurrentPageScene(self):
        """Return QGraphicsScene instance from the active tab widget."""
        for child in self.tabs.currentWidget().children():
            if child.__class__.__name__ == "GraphicsView":
                # return the current scene
                return child.scene()

    def getCurrentPage(self):
        """Return GraphicsView instance from the active tab widget."""
        for child in self.tabs.currentWidget().children():
            if child.__class__.__name__ == "GraphicsView":
                return child

    # need to review
    def mousePressEvent(self, event):
        # is it still in use?
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

    # need to review is it still used?
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.last_point = event.pos()
            print("mouse move and pressed")
            print(self.last_point)

    # need to review is it still used?
    def mouseDoubleClickEvent(self, event):
        self.getCurrentPageScene().editObject()

    # Delete selected objects
    # or edit object
    def keyPressEvent(self, event):
        """Handle main keyboard shortcuts for deleting or editing items."""
        # esc
        if event.key() == Qt.Key.Key_Escape:
            print("escape")
            self.getCurrentPageScene().printObjectDebugInfo()

        # delete an object
        if event.key() == Qt.Key.Key_Delete:
            qm = QMessageBox()
            ret = qm.question(self, _('Delete Object'), _("Are you sure you want to delete those objects?"),
                              qm.StandardButton.Yes | qm.StandardButton.No)

            if ret == qm.StandardButton.No:
                return
            self.getCurrentPageScene().removeItems()
        #edit an object
        elif event.key() == Qt.Key.Key_E:
            self.getCurrentPageScene().editObject()

    def newCopyRight(self):
        """Add copyright text label to current page."""
        self.getCurrentPageScene().newCopyRight()

    def newCopyRightAllPages(self):
        """Add copyright text label across all pages."""
        print("newCopyRightAllPages")
        for x in range(0, self.tabs.count().real):
            self.tabs.setCurrentIndex(x)
            self.getCurrentPageScene().newCopyRight()

    def newImage(self):
        """Prompt user for image file and add it to the scene."""
        options = QFileDialog.Option.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Select picture", "",
                                                  ("all pictures (*.jpg *.jpeg *.png);;PNG (*.png)" ),
                                                  options=options)
        self.getCurrentPageScene().addImage(fileName)

    def str_to_bool(self, s):
        """Convert string boolean representations to Python bool."""
        if s == 'True':
            return True
        elif s == 'False':
            return False
        else:
            raise ValueError

    def configApp(self):
        """Open application configuration dialog."""
        print("config")
        dlg = ConfigDlg()
        res = dlg.exec()

        #Accepted
        if res == 1:
            print("Clicked ok")

