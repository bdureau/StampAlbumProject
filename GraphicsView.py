
"""
Graphics View Module
--------------------
Handles custom QGraphicsView display, scene scaling, object serialization,
deserialization, and clipboard actions (Copy, Cut, Paste).

Author: Boris du Reau
"""

from PyQt6.QtCore import QPointF, Qt, QPoint, QByteArray, QRectF
from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtWidgets import (
    QMessageBox, QGraphicsPixmapItem,
    QGraphicsRectItem,
    QGraphicsScene, QFileDialog, QGraphicsView, QApplication, QLabel, QMainWindow, QMenuBar, QMenu,
    QToolBar,  QGraphicsTextItem, QGraphicsItemGroup, QDialog, QPushButton,
    QLineEdit, QFormLayout, QStatusBar, QTabWidget, QWidget, QVBoxLayout, QDialogButtonBox, QPlainTextEdit
)
from PyQt6.QtGui import QBrush, QPainter, QPen, QPixmap, QPolygonF, QImage, QIcon, QColor, QFont, QTextCursor, \
    QAction, QTextBlockFormat, QShortcut

from PyQt6.QtPrintSupport import QPrintPreviewDialog, QPrinter, QPrintDialog
import importlib
custom_mimeType = "application/x-qgraphicsitems"


# serialise the item
def item_to_ds(it, ds):
    """
        Serialize a QGraphicsItem instance into a QDataStream for clipboard operations.

        Args:
            it (QtWidgets.QGraphicsItem): Item to serialize.
            ds (QtCore.QDataStream): Stream to write data to.
    """
    if not isinstance(it, QtWidgets.QGraphicsItem):
        return

    # Write class module and type name
    ds.writeQString(it.__class__.__module__)
    ds.writeQString(it.__class__.__name__)

    # Write item flags as an integer
    # Safe int conversion for flags in PyQt6
    flags_val = int(it.flags().value) if hasattr(it.flags(), 'value') else int(it.flags())
    ds.writeInt(flags_val)

    # Write position and item custom identifier
    ds << it.pos()
    ds.writeQString(str(it.data(0)) if it.data(0) is not None else "")

    # Handle standard text items
    if it.__class__.__name__ == "QGraphicsTextItem":
        ds.writeQString(it.toPlainText())
        ds.writeBool(it.font().bold())
        ds.writeBool(it.font().italic())
        ds.writeBool(it.font().strikeOut())
        ds.writeBool(it.font().underline())
        ds.writeInt(it.font().pointSize())

    # Handle stamp group items and their children
    if it.__class__.__name__ == "QGraphicsItemGroup" and it.data(0) == "stampGroup":
        for child in it.childItems():

            # Stamp mount box rectangle
            if child.__class__.__name__ == "QGraphicsRectItem":
                ds.writeQString(child.__class__.__name__)
                ds << child.boundingRect()
                ds << child.pos()
                ds.writeInt(child.pen().width())
                ds << child.pen().color()
                ds.writeInt(int(child.data(1)) if child.data(1) else 0) # box width
                ds.writeInt(int(child.data(2)) if child.data(2) else 0) # box height

            # Stamp text elements (Title, Number, Nominal Value)
            if child.__class__.__name__ == "QGraphicsTextItem":
                ds.writeQString(child.__class__.__name__)
                ds.writeQString(child.toPlainText())
                ds << child.pos()
                # Sécurisation si la scène est None
                font = child.font()
                ds.writeBool(font.bold())
                ds.writeBool(font.italic())
                ds.writeBool(font.strikeOut())
                ds.writeBool(font.underline())
                ds.writeInt(font.pointSize())

            # Stamp image item
            if child.__class__.__name__ == "QGraphicsPixmapItem":
                ds.writeQString(child.__class__.__name__)
                ds.writeQVariant(child.pixmap())
                ds << child.pos()

    # Write transform attributes
    ds.writeFloat(it.opacity())
    ds.writeFloat(it.rotation())
    ds.writeFloat(it.scale())

    # Write shape pens and brushes if applicable
    if isinstance(it, QtWidgets.QAbstractGraphicsShapeItem):
        ds << it.brush() << it.pen()
    if isinstance(it, QtWidgets.QGraphicsPathItem):
        ds << it.path()


def ds_to_item(ds):
    """
        Deserialize a QGraphicsItem instance from a QDataStream.

        Args:
            ds (QtCore.QDataStream): Stream to read data from.

        Returns:
            QtWidgets.QGraphicsItem: Reconstructed graphic item.
    """
    print("ds to item")
    module_name = ds.readQString()
    class_name = ds.readQString()
    mod = importlib.import_module(module_name)
    it = getattr(mod, class_name)()
    flags = QtWidgets.QGraphicsItem.GraphicsItemFlag(ds.readInt())
    pos = QtCore.QPointF()
    ds >> pos
    it.setData(0, ds.readQString())

    # Reconstruct standalone text items
    if class_name == "QGraphicsTextItem":
        it.setPlainText(ds.readQString())
        font = QFont()
        font.setBold(ds.readBool())
        font.setItalic(ds.readBool())
        font.setStrikeOut(ds.readBool())
        font.setUnderline(ds.readBool())
        font.setPointSize(ds.readInt())
        it.setFont(font)

    # Reconstruct stamp group items
    if class_name == "QGraphicsItemGroup" and it.data(0) == "stampGroup":
        # 1. Read QGraphicsRectItem parameters
        class1 = ds.readQString() # Class name
        #print(class1)
        bounding_rect = QtCore.QRectF()
        ds >> bounding_rect
        #print(bounding_rect)
        pos1 = QtCore.QPointF()
        ds >> pos1
        #print(pos1)
        pen = QPen()
        pen.setWidth(ds.readInt())
        penColor = QtGui.QColor()
        ds >> penColor
        pen.setColor(penColor)
        #print("done with pen")
        boxW = ds.readInt()
        boxWidth = boxW / (25.4 / 96.0)
        boxH = ds.readInt()
        boxHeight = boxH / (25.4 / 96.0)

        # 2. Read stamp description text
        class2 = ds.readQString()
        #print(class2)
        pos2 = QtCore.QPointF()
        desc = ds.readQString()
        ds >> pos2
        font2 = QFont()
        font2.setBold(ds.readBool())
        font2.setItalic(ds.readBool())
        font2.setStrikeOut(ds.readBool())
        font2.setUnderline(ds.readBool())
        font2.setPointSize(ds.readInt())

        # 3. Read stamp number text
        class3 = ds.readQString()
        #print(class3)
        pos3 = QtCore.QPointF()
        nbr = ds.readQString()
        ds >> pos3
        font3 = QFont()
        font3.setBold(ds.readBool())
        font3.setItalic(ds.readBool())
        font3.setStrikeOut(ds.readBool())
        font3.setUnderline(ds.readBool())
        font3.setPointSize(ds.readInt())

        # 4. Read stamp value text
        class4 = ds.readQString()
        #print(class4)
        pos4 = QtCore.QPointF()
        value = ds.readQString()
        ds >> pos4
        font4 = QFont()
        font4.setBold(ds.readBool())
        font4.setItalic(ds.readBool())
        font4.setStrikeOut(ds.readBool())
        font4.setUnderline(ds.readBool())
        font4.setPointSize(ds.readInt())

        # 5. Read pixmap image
        class5 = ds.readQString()
        #print(class5)
        pos5 = QtCore.QPointF()
        pixmap = ds.readQVariant()
        ds >> pos5

        # Re-assemble stamp description
        stampDesc = QGraphicsTextItem(desc)
        stampDesc.setData(0, "stampDesc")
        stampDesc.setPos(pos2.x(), pos2.y())
        stampDesc.setFont(font2)
        stampDesc.setFlags(QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable |
                           QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable)
        #print("created desc")
        stampDesc.setTextWidth(stampDesc.boundingRect().size().width())
        cursor = stampDesc.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        format = QTextBlockFormat()
        format.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cursor.mergeBlockFormat(format)
        cursor.clearSelection()
        stampDesc.setTextCursor(cursor)

        # Re-assemble stamp box
        stampBox = QGraphicsRectItem(0, 0, boxWidth, boxHeight)
        stampBox.setPos(pos2.x() + (stampDesc.boundingRect().size().width() / 2) - (boxWidth/2),
                        pos2.y() + stampDesc.boundingRect().size().height() +20)

        stampBox.setPen(pen)
        stampBox.setFlags(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable |
                          QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable)
        stampBox.setData(0, "stampBox")
        stampBox.setData(1, boxW)
        stampBox.setData(2, boxH)
        #rint("created box")

        # Re-assemble stamp image and calculate scale factor
        pixmapitem = QGraphicsPixmapItem(pixmap)
        scale1 = (boxWidth - 4) / (pixmapitem.boundingRect().size().width())
        scale2 = (boxHeight - 4) / (pixmapitem.boundingRect().size().height())

        if scale1 < scale2:
            image_scale = scale1
        else:
            image_scale = scale2
        #print("scale calculated")
        pixmapitem.setScale(image_scale)
        #print("set scale pixmap")

        pixmapitem.setPos(pos2.x() + (stampDesc.boundingRect().size().width() / 2) - (image_scale * pixmapitem.boundingRect().size().width() / 2),
                          pos2.y() + stampDesc.boundingRect().size().height() + 20 + (boxHeight / 2 - (image_scale * pixmapitem.boundingRect().size().height()) / 2))
        pixmapitem.setData(0, "pixmapItem")

        # Re-assemble stamp number
        stampNbr = QGraphicsTextItem(nbr)
        stampNbr.setData(0, "stampNbr")

        stampNbr.setFlags(QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable |
                          QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable)


        stampNbr.setTextWidth(stampNbr.boundingRect().size().width())
        cursor = stampNbr.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        format = QTextBlockFormat()
        format.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cursor.mergeBlockFormat(format)
        cursor.clearSelection()
        stampNbr.setTextCursor(cursor)

        stampNbr.setPos(pos2.x() + stampDesc.boundingRect().size().width() / 2 - stampNbr.boundingRect().size().width() / 2,
                        pos2.y() + stampDesc.boundingRect().size().height() + 20 + boxHeight)

        # Re-assemble stamp nominal value
        stampValue = QGraphicsTextItem(value)
        stampValue.setData(0, "stampValue")
        stampValue.setFlags(QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable |
                            QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable)

        #print("created value")
        stampValue.setTextWidth(stampValue.boundingRect().size().width())
        cursor = stampValue.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        format = QTextBlockFormat()
        format.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cursor.mergeBlockFormat(format)
        cursor.clearSelection()
        stampValue.setTextCursor(cursor)

        stampValue.setPos(
             pos2.x() + (stampDesc.boundingRect().size().width() / 2) - (stampValue.boundingRect().size().width() / 2),
             pos2.y() + stampDesc.boundingRect().size().height() + 20 + boxHeight +
             stampNbr.boundingRect().size().height() + 0)

        # Group components into the master item
        it.addToGroup(stampBox)
        it.addToGroup(stampDesc)
        it.addToGroup(stampNbr)
        it.addToGroup(stampValue)
        it.addToGroup(pixmapitem)
        it.setFlags(QGraphicsItemGroup.GraphicsItemFlag.ItemIsMovable |
                    QGraphicsItemGroup.GraphicsItemFlag.ItemIsSelectable)

    # Restore generic item properties
    it.setFlags(flags)
    it.setPos(pos)
    it.setOpacity(ds.readFloat())
    it.setRotation(ds.readFloat())
    it.setScale(ds.readFloat())

    if isinstance(it, QtWidgets.QAbstractGraphicsShapeItem):
        pen, brush = QtGui.QPen(), QtGui.QBrush()
        ds >> brush
        ds >> pen
        it.setPen(pen)
        it.setBrush(brush)
    if isinstance(it, QtWidgets.QGraphicsPathItem):
        path = QtGui.QPainterPath()
        ds >> path
        it.setPath(path)

    #print("end of DS to item")
    return it


class GraphicsView(QtWidgets.QGraphicsView):
    """Custom QGraphicsView with dynamic scaling and clipboard support."""
    def __init__(self, parent=None):
        """Initialize viewport rendering options and keyboard shortcuts."""
        super().__init__(parent)
        self.setScene(parent)

        # Enable smooth anti-aliased rendering during scaling
        self.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform)


        # Enable horizontal and vertical scrollbars when scene overflows viewport
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        #self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Bind standard Copy and Paste shortcuts
        QShortcut(
            QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.Copy),
            self,
            activated=self.copy_items
        )
        QShortcut(
             QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.Paste),
             self,
             activated=self.paste_items,
        )

    def resizeEvent(self, event):
        """Re-evaluate scene scale ratio on viewport resize."""
        super().resizeEvent(event)

        if self.scene():
            # Récupère la largeur disponible dans la vue (moins la largeur de la scrollbar si présente)
            viewport_width = self.viewport().width()
            scene_width = self.scene().sceneRect().width()

            if scene_width > 0:
                # Maintain aspect ratio based on available viewport width
                #scale_factor = viewport_width / scene_width

                # Exemple : on fixe une échelle minimale de 1.0 (ou 0.8)
                min_scale = 1.0
                scale_factor = max(viewport_width / scene_width, min_scale)

                # Réinitialise la transformation et applique l'échelle identique en X et Y (pour garder le ratio)
                self.resetTransform()
                self.scale(scale_factor, scale_factor)

    @QtCore.pyqtSlot()
    def copy_items(self):
        """Serialize selected items and copy them to the system clipboard."""
        print("Copy")
        mimedata = QtCore.QMimeData()
        ba = QtCore.QByteArray()
        ds = QtCore.QDataStream(ba, QtCore.QIODevice.OpenModeFlag.WriteOnly)
        for it in self.scene().selectedItems():
            item_to_ds(it, ds)

        mimedata.setData(custom_mimeType, ba)
        clipboard = QtGui.QGuiApplication.clipboard()
        clipboard.setMimeData(mimedata)

    @QtCore.pyqtSlot()
    def paste_items(self):
        """Deserialize items from clipboard and add them to the current scene."""
        #pos2 = QtCore.QPointF(40, 40)

        clipboard = QtGui.QGuiApplication.clipboard()
        mimedata = clipboard.mimeData()
        if mimedata.hasFormat(custom_mimeType):
            ba = mimedata.data(custom_mimeType)
            ds = QtCore.QDataStream(ba)
            while not ds.atEnd():
                it = ds_to_item(ds)
                self.scene().addItem(it)
