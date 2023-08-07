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
    print("item_to_ds")
    if not isinstance(it, QtWidgets.QGraphicsItem):
        return
    print("item_to_ds 1")
    ds.writeQString(it.__class__.__module__)
    ds.writeQString(it.__class__.__name__)
    print("item_to_ds 2")
    # save the flag
    print(it.flags())
    ds.writeInt(it.flags().value)
    #ds.writeQString(it.flags())
    print("item_to_ds 3")
    # save the position of the object
    ds << it.pos()
    # save the comment about the object
    ds.writeQString(it.data(0))
    print(it.data(0))
    # we have a simple text object
    if it.__class__.__name__ == "QGraphicsTextItem":
        print("QGraphicsTextItem")
        ds.writeQString(it.toPlainText())
        # get the font
        ds.writeBool(it.font().bold())
        ds.writeBool(it.font().italic())
        ds.writeBool(it.font().strikeOut())
        ds.writeBool(it.font().underline())
        ds.writeInt(it.font().pointSize())

    # we have a stamp object
    if it.__class__.__name__ == "QGraphicsItemGroup" and it.data(0) == "stampGroup":

        for child in it.childItems():

            if child.__class__.__name__ == "QGraphicsRectItem":
                ds.writeQString(child.__class__.__name__)
                ds << child.boundingRect()
                ds << child.pos()
                ds.writeInt(child.pen().width())
                ds.writeInt(child.pen().color().value())
                ds.writeInt(child.data(1)) #box width
                ds.writeInt(child.data(2)) # box height


            if child.__class__.__name__ == "QGraphicsTextItem":
                ds.writeQString(child.__class__.__name__)
                ds.writeQString(child.toPlainText())
                ds << child.pos()
                ds.writeBool(child.scene().font().bold())
                ds.writeBool(child.scene().font().italic())
                ds.writeBool(child.scene().font().strikeOut())
                ds.writeBool(child.scene().font().underline())
                ds.writeInt(child.scene().font().pointSize())

            if child.__class__.__name__ == "QGraphicsPixmapItem":
                print("QGraphicsPixmapItem")
                ds.writeQString(child.__class__.__name__)
                ds.writeQVariant(child.pixmap())
                ds << child.pos()

    ds.writeFloat(it.opacity())
    ds.writeFloat(it.rotation())
    ds.writeFloat(it.scale())

    if isinstance(it, QtWidgets.QAbstractGraphicsShapeItem):
        ds << it.brush() << it.pen()
        print(it.pen())
        print(it.brush())
    if isinstance(it, QtWidgets.QGraphicsPathItem):
        ds << it.path()



def ds_to_item(ds):
    print("ds to item")
    module_name = ds.readQString()
    class_name = ds.readQString()
    mod = importlib.import_module(module_name)
    it = getattr(mod, class_name)()
    flags = QtWidgets.QGraphicsItem.GraphicsItemFlag(ds.readInt())
    pos = QtCore.QPointF()
    ds >> pos
    it.setData(0, ds.readQString())
    if class_name == "QGraphicsTextItem":
        it.setPlainText(ds.readQString())
        font = QFont()
        font.setBold(ds.readBool())
        font.setItalic(ds.readBool())
        font.setStrikeOut(ds.readBool())
        font.setUnderline(ds.readBool())
        font.setPointSize(ds.readInt())
        it.setFont(font)

    if class_name == "QGraphicsItemGroup" and it.data(0) == "stampGroup":
        # QGraphicsRectItem
        class1 = ds.readQString()
        print(class1)
        bounding_rect = QtCore.QRectF()
        ds >> bounding_rect
        print(bounding_rect)
        pos1 = QtCore.QPointF()
        ds >> pos1
        print(pos1)
        pen = QPen()
        pen.setWidth(ds.readInt())
        #pen.setColor(ds.readInt())
        #not sure how to get the color working !!!
        penC = ds.readInt()
        print(penC)
        print("done with pen")
        boxW = ds.readInt()
        boxWidth = boxW / (25.4 / 96.0)
        boxH = ds.readInt()
        boxHeight = boxH / (25.4 / 96.0)

        # QGraphicsTextItem
        class2 = ds.readQString()
        print(class2)
        pos2 = QtCore.QPointF()
        desc = ds.readQString()
        ds >> pos2
        font2 = QFont()
        font2.setBold(ds.readBool())
        font2.setItalic(ds.readBool())
        font2.setStrikeOut(ds.readBool())
        font2.setUnderline(ds.readBool())
        font2.setPointSize(ds.readInt())

        # QGraphicsTextItem
        class3 = ds.readQString()
        print(class3)
        pos3 = QtCore.QPointF()
        nbr = ds.readQString()
        ds >> pos3
        font3 = QFont()
        font3.setBold(ds.readBool())
        font3.setItalic(ds.readBool())
        font3.setStrikeOut(ds.readBool())
        font3.setUnderline(ds.readBool())
        font3.setPointSize(ds.readInt())

        # QGraphicsTextItem
        class4 = ds.readQString()
        print(class4)
        pos4 = QtCore.QPointF()
        value = ds.readQString()
        ds >> pos4
        font4 = QFont()
        font4.setBold(ds.readBool())
        font4.setItalic(ds.readBool())
        font4.setStrikeOut(ds.readBool())
        font4.setUnderline(ds.readBool())
        font4.setPointSize(ds.readInt())

        # QGraphicsPixmapItem
        class5 = ds.readQString()
        print(class5)
        pos5 = QtCore.QPointF()
        pixmap = ds.readQVariant()
        ds >> pos5


        stampDesc = QGraphicsTextItem(desc)
        stampDesc.setData(0, "stampDesc")
        stampDesc.setPos(pos2.x(), pos2.y())
        stampDesc.setFont(font2)
        #print(stampDesc.boundingRect().size().width())
        stampDesc.setFlags(QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable |
                           QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable)
        print("created desc")
        stampDesc.setTextWidth(stampDesc.boundingRect().size().width())
        cursor = stampDesc.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        format = QTextBlockFormat()
        format.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cursor.mergeBlockFormat(format)
        cursor.clearSelection()
        stampDesc.setTextCursor(cursor)

        #stampBox = QGraphicsRectItem(0, 0, bounding_rect.width(), bounding_rect.height())
        stampBox = QGraphicsRectItem(0, 0, boxWidth, boxHeight)

        #stampBox.setPos(pos1.x(), pos1.y())
        stampBox.setPos(pos2.x() + (stampDesc.boundingRect().size().width() / 2) - (boxWidth/2),
                        pos2.y() + stampDesc.boundingRect().size().height() +20)
                        #pos1.y())
        ##boxPen = QPen()
        ##boxPen.setColor(Qt.black)
        ##boxPen.setWidth(1)
        stampBox.setPen(pen)

        stampBox.setFlags(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable |
                          QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable)
        stampBox.setData(0, "stampBox")
        stampBox.setData(1, boxW)
        stampBox.setData(2, boxH)
        print("created box")

        pixmapitem = QGraphicsPixmapItem(pixmap)
        print("got pixmap")

        #print(stampBox.boundingRect().size().width())
        #print(pixmapitem.boundingRect().size().width())
        # calculate scale
        #scale1 = (stampBox.boundingRect().size().width() - 4) / (pixmapitem.boundingRect().size().width())
        #scale2 = (stampBox.boundingRect().size().height() - 4) / (pixmapitem.boundingRect().size().height())

        scale1 = (boxWidth - 4) / (pixmapitem.boundingRect().size().width())
        scale2 = (boxHeight - 4) / (pixmapitem.boundingRect().size().height())

        if scale1 < scale2:
            image_scale = scale1
        else:
            image_scale = scale2
        print("scale calculated")
        pixmapitem.setScale(image_scale)
        print("set scale pixmap")
        #pixmapitem.setPos(0 + stampBox.boundingRect().size().width() / 2 - (image_scale * pixmapitem.boundingRect().size().width()) / 2, 0)
        #pixmapitem.setPos(pos5.x(), pos5.y())
        pixmapitem.setPos(pos2.x() + (stampDesc.boundingRect().size().width() / 2) - (image_scale * pixmapitem.boundingRect().size().width() / 2),
                          pos2.y() + stampDesc.boundingRect().size().height() + 20 + (boxHeight / 2 - (image_scale * pixmapitem.boundingRect().size().height()) / 2))
        #boxHeight / 2 - (image_scale * childItem.boundingRect().size().height()) / 2
                          #pos5.y())
        pixmapitem.setData(0, "pixmapItem")

        print("created pixmap")
        stampNbr = QGraphicsTextItem(nbr)
        stampNbr.setData(0, "stampNbr")

        stampNbr.setFlags(QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable |
                          QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable)
        #stampNbr.setPos(0 + stampBox.boundingRect().size().width() / 2 - stampNbr.boundingRect().size().width() / 2, 0 + stampBox.boundingRect().size().height())

        #print("created nbr")

        stampNbr.setTextWidth(stampNbr.boundingRect().size().width())
        cursor = stampNbr.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        format = QTextBlockFormat()
        format.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cursor.mergeBlockFormat(format)
        cursor.clearSelection()
        stampNbr.setTextCursor(cursor)
        #stampNbr.setPos(pos3.x(), pos3.y())
        stampNbr.setPos(pos2.x() + stampDesc.boundingRect().size().width() / 2 - stampNbr.boundingRect().size().width() / 2,
                        pos2.y() + stampDesc.boundingRect().size().height() + 20 + boxHeight)


        stampValue = QGraphicsTextItem(value)
        stampValue.setData(0, "stampValue")
        stampValue.setFlags(QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable |
                            QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable)

        print("created value")
        stampValue.setTextWidth(stampValue.boundingRect().size().width())
        cursor = stampValue.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        format = QTextBlockFormat()
        format.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cursor.mergeBlockFormat(format)
        cursor.clearSelection()
        stampValue.setTextCursor(cursor)
        #stampValue.setPos(pos4.x(), pos4.y())
        stampValue.setPos(
             pos2.x() + (stampDesc.boundingRect().size().width() / 2) - (stampValue.boundingRect().size().width() / 2),
             pos2.y() + stampDesc.boundingRect().size().height() + 20 + boxHeight +
             stampNbr.boundingRect().size().height() + 0)
        # stampValue.setPos(
        #     0 + boxWidth / 2 - stampValue.boundingRect().size().width() / 2,
        #     stampDesc.boundingRect().size().height() + 20 + boxHeight +
        #     stampNbr.boundingRect().size().height() + 0)

        #group = QGraphicsItemGroup()
        it.addToGroup(stampBox)
        it.addToGroup(stampDesc)
        it.addToGroup(stampNbr)
        it.addToGroup(stampValue)
        it.addToGroup(pixmapitem)
        it.setFlags(QGraphicsItemGroup.GraphicsItemFlag.ItemIsMovable |
                    QGraphicsItemGroup.GraphicsItemFlag.ItemIsSelectable)
        #it.setData(0, "stampGroup")
        #group.setPos(pos)

        print("end of stamp")

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

    print("end of DS to item")
    return it


class GraphicsView(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        #self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)

        self.setScene(parent)

        print(self.scene().getPageName())


        QShortcut(
             QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.Copy), self, activated=self.copy_items
         )
        QShortcut(
             QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.Paste),
             self,
             activated=self.paste_items,
        )

    @QtCore.pyqtSlot()
    def copy_items(self):
        print("Copy")
        mimedata = QtCore.QMimeData()
        ba = QtCore.QByteArray()
        ds = QtCore.QDataStream(ba, QtCore.QIODevice.OpenModeFlag.WriteOnly)
        print("Copy1")
        for it in self.scene().selectedItems():
            print("Copy1-1")
            item_to_ds(it, ds)
        print("Copy2")
        mimedata.setData(custom_mimeType, ba)
        clipboard = QtGui.QGuiApplication.clipboard()
        clipboard.setMimeData(mimedata)

    @QtCore.pyqtSlot()
    def paste_items(self):
        pos2 = QtCore.QPointF(40, 40)

        clipboard = QtGui.QGuiApplication.clipboard()
        mimedata = clipboard.mimeData()
        if mimedata.hasFormat(custom_mimeType):
            ba = mimedata.data(custom_mimeType)
            ds = QtCore.QDataStream(ba)
            while not ds.atEnd():
                it = ds_to_item(ds)
                self.scene().addItem(it)
