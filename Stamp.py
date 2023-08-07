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
        pixmapitem.setData(0, "pixmapItem")

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
        print("createStampPix")
        #print(boxWidth)
        #print(boxHeight)
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
        stampDesc.setPos(0,0)

        stampDesc.setFlags(QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable | QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable)
        print("created desc")

        ##stampBox = QGraphicsRectItem(0, 0,  boxWidth / (25.4 / 96.0), boxHeight / (25.4 / 96.0))
        stampBox = QGraphicsRectItem(0, 0, boxWidth / (25.4 / 96.0), boxHeight / (25.4 / 96.0))

        boxPen = QPen()
        boxPen.setWidth(1)
        stampBox.setPen(boxPen)
        #print(stampDesc.boundingRect().size().height())
        stampBox.setFlags(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable | QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable)
        #stampBox.setPos((stampDesc.boundingRect().size().width()/2) - (boxWidth / (25.4 / 96.0)/2),
        #                stampDesc.boundingRect().size().height() + 20)

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


    def updateStamp2(self, stampItem, stampObj, scene):
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

    def updateStamp(self, stampItem, stampObj, scene):
        childrenItems = stampItem.childItems()
        boxWidth = stampObj['stampBox_boxWidth'] / (25.4 / 96.0)
        boxHeight = stampObj['stampBox_boxHeight'] / (25.4 / 96.0)
        #stampDescWidth = 0
        #stampDescHeight = 0
        stampNbrHeight = 0
        boxX = 0
        boxY = 0
        posX = stampItem.pos().x()
        posY = stampItem.pos().y()
        print(posX)
        # first lets find the box
        for childItem in childrenItems:
            if childItem.type().real == 3:
                boxX = childItem.x()
                boxY = childItem.y()

        for childItem in childrenItems:
            # 8 is a text item
            # 7 is a pixmap item
            # 3 is a box
            if childItem.type().real == 8:
                # create a dummy object call desc in order to get the new text size!!
                desc = QGraphicsTextItem(stampObj[childItem.data(0) + '_text'])
                childItem.setPlainText(stampObj[childItem.data(0) + '_text'])
                childItem.setTextWidth(desc.boundingRect().size().width())


                cursor = childItem.textCursor()
                cursor.select(QTextCursor.SelectionType.Document)
                format = QTextBlockFormat()
                format.setAlignment(Qt.AlignmentFlag.AlignCenter)
                cursor.mergeBlockFormat(format)
                cursor.clearSelection()
                childItem.setTextCursor(cursor)

                if childItem.data(0) == 'stampDesc':
                    childItem.setPos(boxX + (boxWidth/2) - (childItem.boundingRect().size().width() / 2),
                                 boxY -(childItem.boundingRect().size().height() + 20))
                    childItem.setFlags(QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable
                                       | QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable)
                    #stampItem.setY();
                    #stampItem.boundingRect().setWidth(desc.boundingRect().size().width())
                    #stampItem.childrenBoundingRect().setWidth(desc.boundingRect().size().width())
                    #stampItem.sceneBoundingRect().setWidth(desc.boundingRect().size().width())

                elif childItem.data(0) == 'stampNbr':
                    childItem.setPos(boxX + (boxWidth / 2) - (childItem.boundingRect().size().width() / 2),
                                     boxY + boxHeight)
                    childItem.setFlags(QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable |
                                       QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable)
                    stampNbrHeight = childItem.boundingRect().size().height()

                elif childItem.data(0) == 'stampValue':
                    childItem.setPos(boxX + (boxWidth / 2) - (childItem.boundingRect().size().width() / 2),
                                     boxY + boxHeight + stampNbrHeight)
                    childItem.setFlags(QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable |
                                       QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable)


            elif childItem.type().real == 7:
                # this is a pixmap
                childItem.setPixmap(stampObj[childItem.data(0) + '_image'])

                # calculate scale
                scale1 = (boxWidth - 4) / (childItem.boundingRect().size().width())
                scale2 = (boxHeight - 4) / (childItem.boundingRect().size().height())

                if scale1 < scale2:
                    image_scale = scale1
                else:
                    image_scale = scale2
                childItem.setScale(image_scale)

                childItem.setPos(boxX + boxWidth / 2 - (
                        image_scale * childItem.boundingRect().size().width()) / 2,
                        boxY + boxHeight / 2 - (image_scale * childItem.boundingRect().size().height()) / 2)


            elif childItem.type().real == 3:
                print("we have a box")
                childItem.setFlags(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable |
                                   QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable)

                childItem.setRect(0, 0, boxWidth, boxHeight)
                childItem.setData(1, stampObj['stampBox_boxWidth'])
                childItem.setData(2, stampObj['stampBox_boxHeight'])

        # let's remove and re-add all items so that it recalculate the group
        group = QGraphicsItemGroup()


        #group.sceneBoundingRect().setWidth()
        #group.childrenBoundingRect().toAlignedRect().
        #group.setY()
        #group.boundingRect().setWidth()
        #group.childrenBoundingRect().setWidth()
        #group.setFlags(QGraphicsItemGroup.ItemClipsChildrenToShape)
        #QGraphicsItemGroup.ItemContainsChildrenInShape
        #stampItem.setPos(posX, posY)
        print(stampItem.pos().x())
        print(stampItem.pos().y())
        print(stampItem.boundingRect().size().width())
        print(stampItem.boundingRect().size().height())
        stampItem.prepareGeometryChange()
        for childItem in childrenItems:
             stampItem.removeFromGroup(childItem)
             stampItem.addToGroup(childItem)
            # print(childItem.data(0))
            # print(childItem.boundingRect().size().width())
            #group.addToGroup(childItem)
        #stampItem.mapToScene(posX, posY)
        #stampItem.mapFromScene(posX, posY)
        stampItem.mapToScene(posX, posY)
        stampItem.mapToParent(posX, posY)

        # group.setFlags(QGraphicsItemGroup.GraphicsItemFlag.ItemIsMovable |
        #                QGraphicsItemGroup.GraphicsItemFlag.ItemIsSelectable)
        # group.setData(0, "stampGroup")
        #stampItem.setPos(posX, posY)
        #group.setPos(posX, posY)
        #group.setPos(0, 0)
        #stampItem.boundingRect().setWidth(200)
        # print(group.boundingRect().size().width())
        # group.boundingRect().size().setWidth(200.0)
        #group.prepareGeometryChange()
        #stampItem.setX(stampItem.pos().x() -((282-153)/2))
        print(stampItem.x())
        print(stampItem.y())

        print(stampItem.pos().x())
        print(stampItem.pos().y())
        print(stampItem.boundingRect().size().width())
        print(stampItem.boundingRect().size().height())
        #stampItem.boundingRect().size().setWidth(200.0)
        #stampItem.sceneBoundingRect().setWidth(200.0)
        #stampItem.setFlags(QGraphicsItemGroup.ItemIsMovable | QGraphicsItemGroup.ItemIsSelectable )
                           #|
                           #QGraphicsItemGroup.ItemContainsChildrenInShape |
                           #QGraphicsItemGroup.ItemClipsToShape |
                          # QGraphicsItemGroup.ItemPositionChange)
        #stampItem.setPos(posX, posY)
        #print(stampItem.boundingRect().size().width())
        #print(stampItem.sceneBoundingRect().width())
        #stampItem.boundingRect().size().setWidth(200.0)
        #myScene = stampItem.scene()

        #myScene.removeItem(stampItem)
        #myScene.addItem(group)
        ####scene.removeItem(stampItem)
        #scene_point = scene.graphicsView_CameraFeed.mapToScene(0, 0)


        #box = QGraphicsRectItem(scene_point.x(), scene_point.y(), w, h)
        ##scene.addItem(group)
        #group.prepareGeometryChange()
        #group.setPos(scene_point.x(), scene_point.y())
        stampItem.boundingRect().adjust(0,200,0, 200)
        stampItem.sceneBoundingRect().adjust(0,200,0, 200)
        stampItem.childrenBoundingRect().toAlignedRect().setWidth(100)
        stampItem.prepareGeometryChange()
        stampItem.childrenBoundingRect().adjust(0,100,0, 100)
        #group.mapToScene()
        print(group.pos().x())
        print(group.pos().y())
        return stampObj

    def deleteStamp(self):
        print("delete stamp")
