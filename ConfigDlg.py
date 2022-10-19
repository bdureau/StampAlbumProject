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



class ConfigDlg(QDialog):
    def __init__(self, parent=None):
        super(ConfigDlg, self).__init__(parent)
        self.setWindowTitle("Application configuration")
        self.createDlg()

    def createDlg(self):
        print("create dialog")
        self.setWindowModality(Qt.ApplicationModal)
        #self.setWindowTitle("Application configuration")
        self.setWindowFlags(Qt.Dialog)

        # default Copyright

        # default boder type

        # default country

        # default text label font

        # default stamp desc font

        # default stamp nbr font