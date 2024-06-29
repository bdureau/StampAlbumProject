from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtWidgets import (
    QGraphicsRectItem, QGraphicsScene, QGraphicsView, QApplication, QLabel, QMainWindow,
    QMenuBar, QMenu, QToolBar, QGraphicsTextItem,QGraphicsItemGroup, QGraphicsPixmapItem,
    QLineEdit, QPushButton, QDialog, QFormLayout
)
from PyQt6.QtGui import QBrush, QPainter, QPen, QPixmap, QPolygonF, QColor, QTextCursor, QTextBlockFormat, QAction
import json
from EditStampDlg import EditStampDlg

class Stamp:
    def __init__(self):
        print("")


    def createStamp(self, scene, nbr, value, desc, boxWidth, boxHeight, x, y, picture):
        #load picture from disk
        pixmap = QPixmap(picture)

        if pixmap is None:
            print("Pixmap is none")
        self.createStampPix(scene, nbr, value, desc, boxWidth, boxHeight, x, y, pixmap)



    # Create stamp
    def createStampPix(self, scene, nbr, value, desc, boxWidth, boxHeight, x, y, pixmap):
        print("createStampPix")
        stampDesc = QGraphicsTextItem(desc)

        stampDesc.setTextWidth(stampDesc.boundingRect().size().width())

        cursor = stampDesc.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        format = QTextBlockFormat()
        format.setAlignment(Qt.AlignmentFlag.AlignCenter)

        cursor.mergeBlockFormat(format)
        cursor.clearSelection()
        stampDesc.setTextCursor(cursor)
        stampDesc.setData(0, "stampDesc")
        stampDesc.setPos(0, 0)
        #stampDesc.setPos(x, y)

        stampDesc.setFlags(QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable | QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable)
        print("created desc")

        stampBox = QGraphicsRectItem(0, 0, boxWidth / (25.4 / 96.0), boxHeight / (25.4 / 96.0))

        boxPen = QPen()
        boxPen.setWidth(1)
        stampBox.setPen(boxPen)

        stampBox.setFlags(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable | QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable)

        stampBox.setPos((stampDesc.boundingRect().size().width() / 2) - (boxWidth / (25.4 / 96.0) / 2),
                        stampDesc.boundingRect().size().height() + 20)
        stampBox.setData(0, "stampBox")
        stampBox.setData(1, boxWidth)
        stampBox.setData(2, boxHeight)

        pixmapitem = QGraphicsPixmapItem(pixmap)

        #calculate scale
        scale1 = (stampBox.boundingRect().size().width() - 4) / (pixmapitem.boundingRect().size().width())
        scale2 = (stampBox.boundingRect().size().height() - 4) / (pixmapitem.boundingRect().size().height())

        if scale1 < scale2:
            image_scale = scale1
        else:
            image_scale = scale2

        print("image_scale")
        print(image_scale)
        pixmapitem.setScale(image_scale)

        pixmapitem.setPos(stampBox.x() + stampBox.boundingRect().size().width() / 2 - (
                    image_scale * pixmapitem.boundingRect().size().width()) / 2,
                          stampBox.y() + stampBox.boundingRect().size().height() / 2 - (
                    image_scale * pixmapitem.boundingRect().size().height()) / 2)
        pixmapitem.setData(0, "pixmapItem")


        stampNbr = QGraphicsTextItem(nbr)
        stampNbr.setData(0, "stampNbr")
        stampNbr.setFlags(QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable | QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable)

        stampNbr.setPos(0 + stampDesc.boundingRect().size().width() / 2 - stampNbr.boundingRect().size().width() / 2,
                        stampDesc.boundingRect().size().height() + 20 + stampBox.boundingRect().size().height())


        stampValue = QGraphicsTextItem(value)
        stampValue.setData(0, "stampValue")
        stampValue.setFlags(QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable | QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable)

        stampValue.setPos(0 + stampDesc.boundingRect().size().width() / 2 - stampValue.boundingRect().size().width() / 2,
                          stampDesc.boundingRect().size().height() + 20 + stampBox.boundingRect().size().height() +
                          stampNbr.boundingRect().size().height() + 0)

        group = QGraphicsItemGroup()
        group.addToGroup(stampBox)
        group.addToGroup(stampDesc)
        group.addToGroup(stampNbr)
        group.addToGroup(stampValue)
        group.addToGroup(pixmapitem)
        group.setFlags(QGraphicsItemGroup.GraphicsItemFlag.ItemIsMovable |
                       QGraphicsItemGroup.GraphicsItemFlag.ItemIsSelectable)
        group.setData(0, "stampGroup")
        group.setPos(x, y)
        scene.addItem(group)
        #group.mapToScene(0, 0)
        #group.setPos(x, y)


    def readStamp(self, stampItem):

        stampObj = {}
        childrenItems = stampItem.childItems()
        for childItem in childrenItems:
            print(childItem.type().real)
            print(childItem.data(0))
            # 8 is a text item
            # 7 is a pixmap item
            # 3 is a box
            if childItem.type().real == 8:
                print(childItem.toPlainText())
                stampObj[childItem.data(0) + '_text'] = childItem.toPlainText()
            elif childItem.type().real == 7:
                stampObj[childItem.data(0) + '_image'] = childItem.pixmap()
                print(childItem.pixmap())
                stampObj[childItem.data(0) + '_width'] = childItem.boundingRect().width()
                stampObj[childItem.data(0) + '_height'] = childItem.boundingRect().height()
                print(childItem.boundingRect().width())
                print(childItem.boundingRect().height())
            elif childItem.type().real == 3:
                print("we have a box")
                print(childItem.boundingRect().width())
                print(childItem.boundingRect().height())
                stampObj[childItem.data(0) + '_width'] = childItem.boundingRect().width()
                stampObj[childItem.data(0) + '_height'] = childItem.boundingRect().height()
                stampObj[childItem.data(0) + '_boxWidth'] = int(childItem.data(1))
                stampObj[childItem.data(0) + '_boxHeight'] = int(childItem.data(2))

        print(stampObj)
        return stampObj


    def updateStamp(self, stampItem, stampObj, scene):
        posX = stampItem.pos().x()
        posY = stampItem.pos().y()
        boxWidth = stampObj['stampBox_boxWidth']
        boxHeight = stampObj['stampBox_boxHeight']
        nbr = stampObj['stampNbr_text']
        value = stampObj['stampValue_text']
        desc = stampObj['stampDesc_text']
        pixmap = stampObj['pixmapItem_image']
        scene.removeItem(stampItem)
        self.createStampPix(scene, nbr, value, desc, boxWidth, boxHeight, posX, posY, pixmap)


    def deleteStamp(self):
        print("delete stamp")
