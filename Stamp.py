"""
Stamp Module
------------
Manages the creation, positioning, rendering, reading, and updating of
grouped stamp items on a QGraphicsScene.

Author: Boris du Reau
"""
import gettext
from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtWidgets import (
    QGraphicsRectItem, QGraphicsScene, QGraphicsView, QApplication, QLabel, QMainWindow,
    QMenuBar, QMenu, QToolBar, QGraphicsTextItem,QGraphicsItemGroup, QGraphicsPixmapItem,
    QLineEdit, QPushButton, QDialog, QFormLayout
)
from PyQt6.QtGui import QBrush, QPainter, QPen, QPixmap, QPolygonF, QColor, QTextCursor, QTextBlockFormat, QAction
import json
from EditStampDlg import EditStampDlg
# Set up gettext localization

gettext.find("Stamp")
translate = gettext.translation('Stamp', localedir='locale', languages=['fr'], fallback=True)
translate.install()
_ = translate.gettext

class Stamp:
    """Helper class providing methods to generate and modify stamp graphic groups."""
    def __init__(self):
        pass


    def createStamp(self, scene, nbr, value, desc, boxWidth, boxHeight, x, y, picture):
        """
                Load an image file from disk and pass it to createStampPix.

                Args:
                    scene: Active QGraphicsScene instance.
                    nbr (str): Stamp catalogue number.
                    value (str): Nominal value text.
                    desc (str): Description title text.
                    boxWidth (float): Stamp mount width in millimeters.
                    boxHeight (float): Stamp mount height in millimeters.
                    x (float): Scene target X coordinate.
                    y (float): Scene target Y coordinate.
                    picture (str): Path to image asset file.
                """
        pixmap = QPixmap(picture)

        if pixmap is None:
            print("Pixmap is none")
        self.createStampPix(scene, nbr, value, desc, boxWidth, boxHeight, x, y, pixmap)

    def createStampPix(self, scene, nbr, value, desc, boxWidth, boxHeight, x, y, pixmap):
        """
        Creates and adds a stamp item group to the scene.

        Args:
            scene: The QGraphicsScene instance.
            nbr (str): Stamp number text.
            value (str): Stamp nominal value text.
            desc (str): Stamp description text.
            boxWidth (float): Width of the stamp mount box in mm.
            boxHeight (float): Height of the stamp mount box in mm.
            x (float): Target X coordinate in the scene.
            y (float): Target Y coordinate in the scene.
            pixmap (QPixmap): Image asset for the stamp.
        """
        # 1. Create description item (Top text)
        stampDesc = QGraphicsTextItem(desc)
        stampDesc.setTextWidth(stampDesc.boundingRect().size().width())

        cursor = stampDesc.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        blockFormat = QTextBlockFormat()
        blockFormat.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cursor.mergeBlockFormat(blockFormat)
        cursor.clearSelection()
        stampDesc.setTextCursor(cursor)

        stampDesc.setData(0, "stampDesc")
        stampDesc.setPos(0, 0)
        stampDesc.setFlags(
            QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable
        )

        # 2. Create rect box item (mm to pixel conversion)
        px_width = boxWidth / (25.4 / 96.0)
        px_height = boxHeight / (25.4 / 96.0)
        stampBox = QGraphicsRectItem(0, 0, px_width, px_height)

        boxPen = QPen()
        boxPen.setWidth(1)
        stampBox.setPen(boxPen)

        stampBox.setFlags(
            QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable
        )

        # Position box relative to centered description
        box_x = (stampDesc.boundingRect().size().width() / 2) - (px_width / 2)
        box_y = stampDesc.boundingRect().size().height() + 20
        stampBox.setPos(box_x, box_y)
        stampBox.setData(0, "stampBox")
        stampBox.setData(1, boxWidth)
        stampBox.setData(2, boxHeight)

        # 3. Create image pixmap item
        pixmapitem = QGraphicsPixmapItem(pixmap)

        # Calculate scale factor to fit inside the rect box with padding
        if pixmapitem.boundingRect().width() > 0 and pixmapitem.boundingRect().height() > 0:
            scale1 = (stampBox.boundingRect().size().width() - 4) / pixmapitem.boundingRect().size().width()
            scale2 = (stampBox.boundingRect().size().height() - 4) / pixmapitem.boundingRect().size().height()
            image_scale = min(scale1, scale2)
        else:
            image_scale = 1.0

        pixmapitem.setScale(image_scale)

        # Center pixmap inside the box
        pix_x = stampBox.x() + (stampBox.boundingRect().size().width() / 2) - (
                    (image_scale * pixmapitem.boundingRect().size().width()) / 2)
        pix_y = stampBox.y() + (stampBox.boundingRect().size().height() / 2) - (
                    (image_scale * pixmapitem.boundingRect().size().height()) / 2)
        pixmapitem.setPos(pix_x, pix_y)
        pixmapitem.setData(0, "pixmapItem")

        # 4. Create stamp number item (Bottom text 1)
        stampNbr = QGraphicsTextItem(nbr)
        stampNbr.setData(0, "stampNbr")
        stampNbr.setFlags(
            QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable
        )
        nbr_x = (stampDesc.boundingRect().size().width() / 2) - (stampNbr.boundingRect().size().width() / 2)
        nbr_y = stampDesc.boundingRect().size().height() + 20 + stampBox.boundingRect().size().height()
        stampNbr.setPos(nbr_x, nbr_y)

        # 5. Create stamp value item (Bottom text 2)
        stampValue = QGraphicsTextItem(value)
        stampValue.setData(0, "stampValue")
        stampValue.setFlags(
            QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable
        )
        val_x = (stampDesc.boundingRect().size().width() / 2) - (stampValue.boundingRect().size().width() / 2)
        val_y = nbr_y + stampNbr.boundingRect().size().height()
        stampValue.setPos(val_x, val_y)

        # 6. Group all items together
        group = QGraphicsItemGroup()
        group.addToGroup(stampBox)
        group.addToGroup(stampDesc)
        group.addToGroup(stampNbr)
        group.addToGroup(stampValue)
        group.addToGroup(pixmapitem)

        group.setFlags(
            QGraphicsItemGroup.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItemGroup.GraphicsItemFlag.ItemIsSelectable
        )
        group.setData(0, "stampGroup")

        # 7. Normalize child positions so group top-left strictly aligns with (0,0)
        children_rect = group.childrenBoundingRect()
        for child in group.childItems():
            child.moveBy(-children_rect.x(), -children_rect.y())

        # 8. Set final absolute position in scene
        group.setPos(x, y)

        if hasattr(scene, 'addItemWithUndo'):
            scene.addItemWithUndo(group, _("Add Stamp"))
        else:
            scene.addItem(group)

    # Create stamp
    # this can be used for old version
    def createStampPix_old(self, scene, nbr, value, desc, boxWidth, boxHeight, x, y, pixmap):
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
        """
                Extract property text, box dimensions, and pixmap data from a stamp group.

                Args:
                    stampItem: Active QGraphicsItemGroup instance.

                Returns:
                    dict: Dictionary mapping stamp child keys to their corresponding values.
        """
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
                stampObj[childItem.data(0) + '_width'] = childItem.boundingRect().width()
                stampObj[childItem.data(0) + '_height'] = childItem.boundingRect().height()

            elif childItem.type().real == 3:
                stampObj[childItem.data(0) + '_width'] = childItem.boundingRect().width()
                stampObj[childItem.data(0) + '_height'] = childItem.boundingRect().height()
                stampObj[childItem.data(0) + '_boxWidth'] = int(childItem.data(1))
                stampObj[childItem.data(0) + '_boxHeight'] = int(childItem.data(2))

        print(stampObj)
        return stampObj

    def updateStamp(self, stampItem, stampObj, scene):
        # Récupérer le coin supérieur gauche réel dans la scène avant suppression
        top_left = stampItem.sceneBoundingRect().topLeft()

        boxWidth = stampObj['stampBox_boxWidth']
        boxHeight = stampObj['stampBox_boxHeight']
        nbr = stampObj['stampNbr_text']
        value = stampObj['stampValue_text']
        desc = stampObj['stampDesc_text']
        pixmap = stampObj['pixmapItem_image']

        # Supprimer l'ancien groupe
        scene.removeItem(stampItem)

        # Créer le nouveau timbre avec les coordonnées exactes du coin supérieur gauche
        self.createStampPix(scene, nbr, value, desc, boxWidth, boxHeight, top_left.x(), top_left.y(), pixmap)

    def updateStamp_old(self, stampItem, stampObj, scene):
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
