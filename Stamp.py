from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtWidgets import (
    QGraphicsRectItem, QGraphicsScene, QGraphicsView, QApplication, QLabel, QMainWindow,
    QMenuBar, QMenu, QToolBar,QAction,QGraphicsTextItem,QGraphicsItemGroup, QGraphicsPixmapItem,
    QLineEdit,QPushButton,QDialog,QFormLayout
)
from PyQt5.QtGui import QBrush, QPainter, QPen, QPixmap, QPolygonF, QColor, QTextCursor, QTextBlockFormat
import json
from EditStampDlg import EditStampDlg

class Stamp:
    def __init__(self):
        print("")
    #, picture, descFont, valFont, boxAroundNbr, nbrLinesAfterDesc
    # def __init__(self, scene, nbr, value, desc, boxWidth, boxHeight, boxTop, boxLeft, picture):
    #     self.scene = scene
    #     self.nbr = nbr
    #     self.value = value
    #     self.desc = desc
    #     self.boxWidth = boxWidth
    #     self.boxHeight = boxHeight
    #     self.boxTop = boxTop
    #     self.boxLeft = boxLeft
    #     self.picture = picture
    #     # self.descFont = descFont
    #     self.createStamp()


    def createStamp(self, scene, nbr, value, desc, boxWidth, boxHeight, x, y, picture):
        #load picture from disk
        pixmap = QPixmap(picture)

        # print("Pixmap")
        # print(pixmap)
        if pixmap is None:
            print("Pixmap is none")
        self.createStampPix(scene, nbr, value, desc, boxWidth, boxHeight, x, y, pixmap)

    #obsolete
    def createStampPixOld(self, scene, nbr, value, desc, boxWidth, boxHeight, x, y, pixmap):
        stampBox = QGraphicsRectItem(0, 0,  boxWidth / (25.4 / 96.0), boxHeight / (25.4 / 96.0))
        boxPen = QPen()
        boxPen.setColor(Qt.black)
        boxPen.setWidth(2)
        stampBox.setPen(boxPen)

        stampBox.setFlags(QGraphicsRectItem.ItemIsMovable | QGraphicsRectItem.ItemIsSelectable)
        stampBox.setData(0, "stampBox")
        print("created box")

        pixmapitem = QGraphicsPixmapItem(pixmap)

        #calculate scale
        scale1 = stampBox.boundingRect().size().width() / pixmapitem.boundingRect().size().width()
        scale2 = stampBox.boundingRect().size().height() / pixmapitem.boundingRect().size().height()

        if scale1 < scale2:
            image_scale = scale1
        else:
            image_scale = scale2
        pixmapitem.setScale(image_scale)

        pixmapitem.setPos(0+stampBox.boundingRect().size().width()/2-(image_scale*pixmapitem.boundingRect().size().width())/2, 0)
        pixmapitem.setData(0, "pixmapitem")

        stampDesc = QGraphicsTextItem(desc)
        stampDesc.setData(0, "stampDesc")
        stampDesc.setPos(0+stampBox.boundingRect().size().width()/2-stampDesc.boundingRect().size().width()/2, 0-40)
        print(stampDesc.font().pixelSize())
        print(stampDesc.font().pointSize())
        stampDesc.setFlags(QGraphicsTextItem.ItemIsMovable | QGraphicsTextItem.ItemIsSelectable)
        print("created desc")
        stampNbr = QGraphicsTextItem(nbr)
        stampNbr.setData(0, "stampNbr")

        stampNbr.setFlags(QGraphicsTextItem.ItemIsMovable | QGraphicsTextItem.ItemIsSelectable)
        stampNbr.setPos(0 + stampBox.boundingRect().size().width() / 2 - stampNbr.boundingRect().size().width() / 2, 0 + stampBox.boundingRect().size().height())
        print("created nbr")
        stampValue = QGraphicsTextItem(value)
        stampValue.setData(0, "stampValue")
        stampValue.setFlags(QGraphicsTextItem.ItemIsMovable | QGraphicsTextItem.ItemIsSelectable)
        stampValue.setPos(0 + stampBox.boundingRect().size().width() / 2 - stampValue.boundingRect().size().width() / 2, 0 + stampBox.boundingRect().size().height()+ 50)
        print("created value")
        group = QGraphicsItemGroup()
        group.addToGroup(stampBox)
        group.addToGroup(stampDesc)
        group.addToGroup(stampNbr)
        group.addToGroup(stampValue)
        group.addToGroup(pixmapitem)
        #group.addToGroup(stampDesc)
        group.setFlags(QGraphicsItemGroup.ItemIsMovable | QGraphicsItemGroup.ItemIsSelectable)
        group.setData(0, "stampGroup")
        group.setPos(x, y)

        scene.addItem(group)

    # Create stamp
    def createStampPix(self, scene, nbr, value, desc, boxWidth, boxHeight, x, y, pixmap):
        stampDesc = QGraphicsTextItem(desc)

        cursor = stampDesc.textCursor()
        format = QTextBlockFormat()
        format.setAlignment(Qt.AlignCenter)
        cursor.mergeBlockFormat(format)
        stampDesc.setTextCursor(cursor)
        stampDesc.setData(0, "stampDesc")
        stampDesc.setPos(0,0)

        stampDesc.setFlags(QGraphicsTextItem.ItemIsMovable | QGraphicsTextItem.ItemIsSelectable)
        print("created desc")

        stampBox = QGraphicsRectItem(0, 0,  boxWidth / (25.4 / 96.0), boxHeight / (25.4 / 96.0))
        boxPen = QPen()
        boxPen.setWidth(1)
        stampBox.setPen(boxPen)
        print(stampDesc.boundingRect().size().height())
        stampBox.setFlags(QGraphicsRectItem.ItemIsMovable | QGraphicsRectItem.ItemIsSelectable)
        stampBox.setPos((stampDesc.boundingRect().size().width()/2) - (boxWidth / (25.4 / 96.0)/2),
                        stampDesc.boundingRect().size().height() + 20)
        stampBox.setData(0, "stampBox")
        # stampBox.pen().width().real()
        # stampBox.pen().color().value().real()
        print("created box")

        pixmapitem = QGraphicsPixmapItem(pixmap)

        #calculate scale
        scale1 = (stampBox.boundingRect().size().width() - 4) / (pixmapitem.boundingRect().size().width())
        scale2 = (stampBox.boundingRect().size().height() - 4) / (pixmapitem.boundingRect().size().height())

        if scale1 < scale2:
            image_scale = scale1
        else:
            image_scale = scale2
        pixmapitem.setScale(image_scale)

        #pixmapitem.setPos(0+stampBox.boundingRect().size().width()/2-(image_scale*pixmapitem.boundingRect().size().width())/2, 0)
        pixmapitem.setPos(stampBox.x() + stampBox.boundingRect().size().width() / 2 - (
                    image_scale * pixmapitem.boundingRect().size().width()) / 2,
                          stampBox.y() + stampBox.boundingRect().size().height() / 2 - (
                    image_scale * pixmapitem.boundingRect().size().height()) / 2)
        pixmapitem.setData(0, "pixmapitem")


        stampNbr = QGraphicsTextItem(nbr)
        stampNbr.setData(0, "stampNbr")
        stampNbr.setFlags(QGraphicsTextItem.ItemIsMovable | QGraphicsTextItem.ItemIsSelectable)
        #stampNbr.setPos(0 + stampBox.boundingRect().size().width() / 2 - stampNbr.boundingRect().size().width() / 2, 0 + stampBox.boundingRect().size().height())
        stampNbr.setPos(0 + stampDesc.boundingRect().size().width() / 2 - stampNbr.boundingRect().size().width() / 2,
                        stampDesc.boundingRect().size().height() + 20 + stampBox.boundingRect().size().height())
        print("created nbr")

        stampValue = QGraphicsTextItem(value)
        stampValue.setData(0, "stampValue")
        stampValue.setFlags(QGraphicsTextItem.ItemIsMovable | QGraphicsTextItem.ItemIsSelectable)
        #stampValue.setPos(0 + stampBox.boundingRect().size().width() / 2 - stampValue.boundingRect().size().width() / 2, 0 + stampBox.boundingRect().size().height()+ 50)
        stampValue.setPos(0 + stampDesc.boundingRect().size().width() / 2 - stampValue.boundingRect().size().width() / 2,
                          stampDesc.boundingRect().size().height() + 20 + stampBox.boundingRect().size().height() +
                          stampNbr.boundingRect().size().height() + 0)

        print("created value")
        group = QGraphicsItemGroup()
        group.addToGroup(stampBox)
        group.addToGroup(stampDesc)
        group.addToGroup(stampNbr)
        group.addToGroup(stampValue)
        group.addToGroup(pixmapitem)
        group.setFlags(QGraphicsItemGroup.ItemIsMovable | QGraphicsItemGroup.ItemIsSelectable)
        group.setData(0, "stampGroup")
        group.setPos(x, y)

        scene.addItem(group)
    def readStamp(self, stampItem):
        print("edit stamp")
        # items = stampItem.childItems()
        # for item in items:
        #     print(item.type().real)
        print("editing stamp")
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
                #myImage = childItem.toGraphicsObject()
                stampObj[childItem.data(0) + '_image'] = childItem.pixmap()
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

        print(stampObj)
        return stampObj

    def updateStamp(self, stampItem, stampObj):

        print("updating  stamp")
        childrenItems = stampItem.childItems()
        boxWidth = 0
        boxHeight = 0
        boxX = 0
        boxY = 0
        # first lets find the box
        for childItem in childrenItems:
            if childItem.type().real == 3:
                print("box info")
                boxWidth = childItem.boundingRect().size().width()
                boxHeight = childItem.boundingRect().size().height()
                boxX = childItem.x()
                boxY = childItem.y()

        for childItem in childrenItems:
            # 8 is a text item
            # 7 is a pixmap item
            # 3 is a box
            if childItem.type().real == 8:
                print(childItem.toPlainText())

                childItem.setPlainText(stampObj[childItem.data(0) + '_text'])
                cursor = childItem.textCursor()
                format = QTextBlockFormat()
                format.setAlignment(Qt.AlignCenter)
                cursor.mergeBlockFormat(format)
                childItem.setTextCursor(cursor)

                childItem.setPos(boxX + (boxWidth/2) - (childItem.boundingRect().size().width() / 2), childItem.y())

            elif childItem.type().real == 7:
                print("not sure")

                childItem.setPixmap(stampObj[childItem.data(0) + '_image'])

                ##stampObj[childItem.data(0) + '_width'] = childItem.boundingRect().width()
                #childItem.boundingRect().se
                ##stampObj[childItem.data(0) + '_height'] = childItem.boundingRect().height()

            elif childItem.type().real == 3:
                print("we have a box")
                # print(childItem.boundingRect().width())
                # print(childItem.boundingRect().height())
                # stampObj[childItem.data(0) + '_width'] = childItem.boundingRect().width()
                # stampObj[childItem.data(0) + '_height'] = childItem.boundingRect().height()

        print(stampObj)
        return stampObj

    def deleteStamp(self):
        print("delete stamp")
