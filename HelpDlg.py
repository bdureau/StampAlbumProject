from os import walk
from PyQt5.QtCore import QPointF, Qt, QPoint, QByteArray, QRectF
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (
    QMessageBox,
    QGraphicsRectItem,
    QGraphicsScene, QComboBox, QRadioButton, QButtonGroup, QGroupBox, QListWidgetItem,
    QGraphicsView, QApplication, QLabel, QMainWindow, QMenuBar, QMenu, QHBoxLayout, QListView,
    QToolBar, QAction, QGraphicsTextItem, QGraphicsItemGroup, QDialog, QPushButton, QListWidget,QTextBrowser,
    QLineEdit, QFormLayout, QStatusBar, QTabWidget, QWidget, QVBoxLayout, QDialogButtonBox, QPlainTextEdit
)
from PyQt5.QtGui import QFont, QBrush, QPainter, QPen, QPixmap, QPolygonF, QImage, QIcon, QStandardItem, QColor
from PyQt5.QtPrintSupport import QPrintPreviewDialog, QPrinter, QPrintDialog

class HelpDlg(QDialog):
    def __init__(self, parent=None):
        super(HelpDlg, self).__init__(parent)
        self.setWindowTitle("Application Help")

        self.createDlg()

    def createDlg(self):
        print("create dialog")
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.Dialog)
        output = QTextBrowser()
        output.setSource(QtCore.QUrl.fromLocalFile("Help/stamp_album_help.html"))

        # ok /cancel button
        bb = QDialogButtonBox(QDialogButtonBox.Ok)
        bb.accepted.connect(self.accept)


        flo = QFormLayout()
        flo.addRow(output)
        flo.addRow(bb)

        self.setLayout(flo)