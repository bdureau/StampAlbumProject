from os import walk
from PyQt6.QtCore import QPointF, Qt, QPoint, QByteArray, QRectF
from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import (
    QMessageBox,
    QGraphicsRectItem,
    QGraphicsScene, QComboBox, QRadioButton, QButtonGroup, QGroupBox, QListWidgetItem,
    QGraphicsView, QApplication, QLabel, QMainWindow, QMenuBar, QMenu, QHBoxLayout, QListView,
    QToolBar, QGraphicsTextItem, QGraphicsItemGroup, QDialog, QPushButton, QListWidget,QTextBrowser,
    QLineEdit, QFormLayout, QStatusBar, QTabWidget, QWidget, QVBoxLayout, QDialogButtonBox, QPlainTextEdit
)
from PyQt6.QtGui import QFont, QBrush, QPainter, QPen, QPixmap, QPolygonF, QImage, QIcon, QStandardItem, QAction, QColor
from PyQt6.QtPrintSupport import QPrintPreviewDialog, QPrinter, QPrintDialog

class HelpDlg(QDialog):
    def __init__(self, parent=None):
        super(HelpDlg, self).__init__(parent)
        self.setWindowTitle("Application Help")

        self.createDlg()

    def createDlg(self):
        print("create dialog")
        #self.setWindowModality(Qt.ApplicationModal)
        #self.setWindowFlags(Qt.Dialog)
        output = QTextBrowser()
        output.setSource(QtCore.QUrl.fromLocalFile("Help/stamp_album_help.html"))

        # ok /cancel button
        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        bb.accepted.connect(self.accept)


        flo = QFormLayout()
        flo.addRow(output)
        flo.addRow(bb)

        self.setLayout(flo)