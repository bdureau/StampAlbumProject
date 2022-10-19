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
from PyQt5.QtGui import QFont, QBrush, QPainter, QPen, QPixmap, QPolygonF, QImage, QIcon, QStandardItem, QColor
from PyQt5.QtPrintSupport import QPrintPreviewDialog, QPrinter, QPrintDialog



class TextDlg(QDialog):
    def __init__(self, parent=None):
        super(TextDlg, self).__init__(parent)
        self.setWindowTitle("Add new text")
        self.createDlg()

    def createDlg(self):
        print("create dialog")
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

        hLayout1.addWidget(boldButton)
        hLayout1.addWidget(italicButton)
        hLayout1.addWidget(strikeButton)
        hLayout1.addWidget(underlineButton)

        self.fontSize = QComboBox()

        for x in range(100):
            self.fontSize.addItem(str(x))

        self.fontSize.setMaximumWidth(50)

        hLayout1.addWidget(self.fontSize)

        boldButton.clicked.connect(self.boldPushed)
        italicButton.clicked.connect(self.italicPushed)
        strikeButton.clicked.connect(self.strikePushed)
        underlineButton.clicked.connect(self.underlinePushed)

        self.eTXT = QPlainTextEdit()
        self.eTXT.setFixedHeight(80)
        self.eTXT.setPlainText("")
        print(self.eTXT.font().pixelSize())


        myFont = self.eTXT.font()
        self.fontSize.setCurrentText(str(myFont.pointSize()))
        self.fontSize.currentTextChanged.connect(self.fontSizeClicked)

        print(myFont)

        flo = QFormLayout()
        flo.addRow(hLayout1)
        flo.addRow("", self.eTXT)

        self.setLayout(flo)

        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        flo.addWidget(bb)
        self.eTXT.setFocus()
        # res = self.exec_()
        # if res == QDialog.Accepted:
        #     print("Clicked ok")
        #     self.getCurrentPageScene().addTextLabel(self.eTXT.toPlainText())
        #
        # if res == QDialog.Rejected:
        #     print("Clicked cancel")

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
        #myFont.pointSize()
        self.eTXT.setFont(myFont)
