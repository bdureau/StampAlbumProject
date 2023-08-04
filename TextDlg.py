from os import walk
from PyQt5.QtCore import QPointF, Qt, QPoint, QByteArray, QRectF
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (
    QMessageBox,
    QGraphicsRectItem,
    QGraphicsScene, QComboBox, QRadioButton, QButtonGroup, QGroupBox, QListWidgetItem,
    QGraphicsView, QApplication, QLabel, QMainWindow, QMenuBar, QMenu, QHBoxLayout, QListView,
    QToolBar, QAction, QGraphicsTextItem, QGraphicsItemGroup, QDialog, QPushButton, QListWidget,QTextEdit,
    QLineEdit, QFormLayout, QStatusBar, QTabWidget, QWidget, QVBoxLayout, QDialogButtonBox, QPlainTextEdit
)
from PyQt5.QtGui import QFont, QBrush, QPainter, QPen, QPixmap, QPolygonF, QImage, QIcon, QStandardItem, QColor,QTextBlockFormat, QTextCursor
from PyQt5.QtPrintSupport import QPrintPreviewDialog, QPrinter, QPrintDialog

import gettext
gettext.find("TextDlg")
translate = gettext.translation('TextDlg', localedir='locale', languages=['fr'])
translate.install()
_ = translate.gettext

class TextDlg(QDialog):
    def __init__(self, txtObj=None, parent=None):
        super(TextDlg, self).__init__(parent)
        self.setWindowTitle(_("Add new text"))
        self.createDlg(txtObj)

    def createDlg(self, txtObj=None):
        self.setWindowModality(Qt.ApplicationModal)

        self.setWindowFlags(Qt.Dialog)

        hLayout1 = QHBoxLayout()

        boldButton = QPushButton()
        boldButton.setFixedWidth(30)
        boldButton.setIcon(QIcon("images/bold.png"))

        italicButton = QPushButton()
        italicButton.setIcon(QIcon("images/italic.png"))
        italicButton.setFixedWidth(30)

        strikeButton = QPushButton()
        strikeButton.setIcon(QIcon("images/strike.png"))
        strikeButton.setFixedWidth(30)

        underlineButton = QPushButton()
        underlineButton.setIcon(QIcon("images/underline.png"))
        underlineButton.setFixedWidth(30)

        justifyLeftButton = QPushButton()
        justifyLeftButton.setIcon(QIcon("images/justify left.png"))
        justifyLeftButton.setFixedWidth(30)

        centerButton = QPushButton()
        centerButton.setIcon(QIcon("images/justify center.png"))
        centerButton.setFixedWidth(30)

        justifyRightButton = QPushButton()
        justifyRightButton.setIcon(QIcon("images/justify right.png"))
        justifyRightButton.setFixedWidth(30)

        hLayout1.addWidget(boldButton)
        hLayout1.addWidget(italicButton)
        hLayout1.addWidget(strikeButton)
        hLayout1.addWidget(underlineButton)
        hLayout1.addWidget(justifyLeftButton)
        hLayout1.addWidget(centerButton)
        hLayout1.addWidget(justifyRightButton)

        self.fontSize = QComboBox()

        for x in range(100):
            self.fontSize.addItem(str(x))

        self.fontSize.setMaximumWidth(50)

        hLayout1.addWidget(self.fontSize)

        boldButton.clicked.connect(self.boldPushed)
        italicButton.clicked.connect(self.italicPushed)
        strikeButton.clicked.connect(self.strikePushed)
        underlineButton.clicked.connect(self.underlinePushed)

        justifyLeftButton.clicked.connect(self.justifyLeftPushed)
        centerButton.clicked.connect(self.centerPushed)
        justifyRightButton.clicked.connect(self.justifyRightPushed)

        self.eTXT = QTextEdit()
        self.eTXT.setFixedHeight(80)

        myFont = self.eTXT.font()
        self.fontSize.setCurrentText(str(myFont.pointSize()))
        self.fontSize.currentTextChanged.connect(self.fontSizeClicked)

        if txtObj is None:
            self.eTXT.setPlainText("")
        else:
            self.eTXT.setPlainText(txtObj.toPlainText())
            self.eTXT.setFont(txtObj.font())
            #self.eTXT.setAlignment(txtObj.alignment())
            #self.eTXT.setAlignment()
            cursor = txtObj.textCursor()
            cursor.select(QTextCursor.Document)
            format = QTextBlockFormat()
            cursor.mergeBlockFormat(format)
            #cursor.select(format)
            cursor.clearSelection()

            # unfortunately does not get the alignment...
            align = format.alignment()
            #align = Qt.AlignCenter
            print(align)
            self.eTXT.selectAll()
            self.eTXT.setAlignment(align)



        flo = QFormLayout()
        flo.addRow(hLayout1)
        flo.addRow("", self.eTXT)

        self.setLayout(flo)

        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        flo.addWidget(bb)
        self.eTXT.setFocus()


    def boldPushed(self):
        if self.eTXT.font().bold() == True:
            myFont = self.eTXT.font()
            myFont.setBold(False)
            self.eTXT.setFont(myFont)
        else:
            myFont = self.eTXT.font()
            myFont.setBold(True)
            self.eTXT.setFont(myFont)

    def underlinePushed(self):
        if self.eTXT.font().underline() == True:
            myFont = self.eTXT.font()
            myFont.setUnderline(False)
            self.eTXT.setFont(myFont)
        else:
            myFont = self.eTXT.font()
            myFont.setUnderline(True)
            self.eTXT.setFont(myFont)

    def italicPushed(self):
        if self.eTXT.font().italic():
            myFont = self.eTXT.font()
            myFont.setItalic(False)
            self.eTXT.setFont(myFont)
        else:
            myFont = self.eTXT.font()
            myFont.setItalic(True)
            self.eTXT.setFont(myFont)

    def strikePushed(self):
        if self.eTXT.font().strikeOut() == True:
            myFont = self.eTXT.font()
            myFont.setStrikeOut(False)
            self.eTXT.setFont(myFont)
        else:
            myFont = self.eTXT.font()
            myFont.setStrikeOut(True)
            self.eTXT.setFont(myFont)

    def fontSizeClicked(self):
        myFont = self.eTXT.font()
        myFont.setPointSize(int(self.fontSize.currentText()))
        self.eTXT.setFont(myFont)

    def justifyLeftPushed(self):
        print("")
        # set text alignment to AlignLeft
        self.eTXT.setAlignment(Qt.AlignLeft)


    def centerPushed(self):
        print("")
        self.eTXT.setAlignment(Qt.AlignCenter)

    def justifyRightPushed(self):
        print("")
        self.eTXT.setAlignment(Qt.AlignRight)
