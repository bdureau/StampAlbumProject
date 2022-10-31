
from PyQt5.QtCore import QPointF, Qt, QRectF
from PyQt5 import QtCore, QtGui, QtPrintSupport
from PyQt5.QtWidgets import (
    QGraphicsRectItem, QGraphicsScene, QGraphicsView, QApplication,
    QLabel, QMainWindow, QMenuBar, QMenu, QToolBar, QAction,
    QGraphicsTextItem, QGraphicsItemGroup,
    QGraphicsPixmapItem, QDialog, QLineEdit, QPushButton, QFormLayout, QFileDialog
    )
from PyQt5.QtGui import QBrush, QPainter, QPen, QPixmap, QPolygonF, QFont
from PyQt5.QtPrintSupport import QPrintPreviewDialog, QPrinter, QPrintDialog
from StampDlg import StampDlg
from TextDlg import TextDlg
from Stamp import Stamp
from EditStampDlg import EditStampDlg

class Page(QGraphicsScene):
    def __init__(self, pageType = "portrait", border=None, parent=None):
        super(Page, self).__init__(parent)
        self.pageType = pageType
        if pageType == "portrait":
            self.setSceneRect(0, 0, 210 / (25.4 / 96), 297 / (25.4 / 96))
            if border is not None and border:
                self.addBorder(177 / (25.4 / 96.0),
                           272 / (25.4 / 96.0),
                           19 / (25.4 / 96.0),
                           0,
                           #10 / (25.4 / 96.0),
                           0,
                           0)
        else:
            self.setSceneRect(0, 0, 297 / (25.4 / 96), 210 / (25.4 / 96))
            if border is not None and border:
                self.addBorder(272 / (25.4 / 96.0),
                           177 / (25.4 / 96.0),
                           ((297-272) / 2) / (25.4 / 96.0),
                           0,
                           19 / (25.4 / 96.0),
                           0)

    def getPageName(self):
        return ""
    def addBorder(self, boxWidth, boxHeight, margin_left, margin_right, margin_top, margin_bottom):
        print("")
        borderBox = QGraphicsRectItem(0, 0, boxWidth, boxHeight)
        boxPen = QPen()
        boxPen.setColor(Qt.black)
        boxPen.setWidth(1)
        borderBox.setPen(boxPen)
        borderBox.setData(1, boxWidth)
        borderBox.setData(2, boxHeight)
        borderBox.setData(3, margin_left)

        borderBox2 = QGraphicsRectItem(0, 0, boxWidth - 4 - 6, (boxHeight-4-6))
        boxPen2 = QPen()
        boxPen2.setColor(Qt.black)
        boxPen2.setWidth(4)
        borderBox2.setPen(boxPen2)
        borderBox2.setData(1, boxWidth - 4 - 6)
        borderBox2.setData(2, boxHeight - 4 - 6)
        borderBox2.setData(3, margin_left)

        borderBox3 = QGraphicsRectItem(0, 0, boxWidth - 4 - 6 - 9, (boxHeight - 4 - 6 - 9))
        boxPen3 = QPen()
        boxPen3.setColor(Qt.black)
        boxPen3.setWidth(1)
        borderBox3.setPen(boxPen3)
        borderBox3.setData(1, boxWidth - 4 - 6 - 9)
        borderBox3.setData(2, boxHeight - 4 - 6 - 9)
        borderBox3.setData(3, margin_left)

        borderBox2.setPos((borderBox.boundingRect().size().width() -1) / 2 - (borderBox2.boundingRect().size().width() -4) / 2,
                          (borderBox.boundingRect().size().height() -1) / 2 - (borderBox2.boundingRect().size().height()-4) / 2)
        borderBox3.setPos(
            (borderBox.boundingRect().size().width() - 1) / 2 - (borderBox3.boundingRect().size().width() - 1) / 2,
            (borderBox.boundingRect().size().height() - 1) / 2 - (borderBox3.boundingRect().size().height() - 1) / 2)
        group = QGraphicsItemGroup()
        group.addToGroup(borderBox)
        group.addToGroup(borderBox2)
        group.addToGroup(borderBox3)
        print(group.boundingRect().size().height())
        if margin_top != 0:
            margin_top2 = margin_top
        else:
            margin_top2 = (self.height() - group.boundingRect().size().height())/2
        group.setPos(margin_left, margin_top2)
        group.setData(0, "borderGroup")
        group.setData(1, boxWidth)
        group.setData(2, boxHeight)
        group.setData(3, margin_left)
        self.addItem(group)

    def addTextLabel(self, text, x=20, y=20, font=None):
        textLabel = QGraphicsTextItem(text)
        textLabel.setData(0, "textLabel")

        if font is not None:
            textLabel.setFont(font)
        print(textLabel.opacity())
        #textLabel.setOpacity(0.10)
        print(textLabel.font().bold())
        print(textLabel.font().italic())
        print(textLabel.font().pointSize())
        print(textLabel.font().underline())
        print(textLabel.font().pixelSize())


        textLabel.setPos(x, y)
        textLabel.setFlags(QGraphicsTextItem.ItemIsMovable | QGraphicsTextItem.ItemIsSelectable)
        #print(textLabel.data(0))
        textLabel.setSelected(True)
        self.addItem(textLabel)

    def clearPage(self):
        items = self.items()
        for item in items:
            self.removeItem(item)

    def removeItems(self):
        items = self.selectedItems()
        for item in items:
            self.removeItem(item)

    def editObject(self):
        print("editlabel")
        items = self.selectedItems()
        nbrOfItems = 0
        for item in items:
            nbrOfItems = nbrOfItems + 1

        if nbrOfItems > 1:
            print("more than one item selected")
            return

        if nbrOfItems == 0:
            print("no items selected")
            return

        print("We are good to go")
        itemType = 0
        for item in items:
            print(item.type().real)
            itemType = item.type().real

            if itemType == 10:
                print("This is a stamp")
                self.editStamp(item)
            elif itemType == 8:
                print("This is a text label")
                self.editLabel(item)

    def editLabel(self, item):
        print("editing label")

        dlg = TextDlg(item)
        res = dlg.exec_()

        if res == QDialog.Accepted:
            print("Clicked ok")
            text = dlg.eTXT.toPlainText()
            font = dlg.eTXT.font()
            item.setPlainText(text)
            item.setFont(font)

        if res == QDialog.Rejected:
            print("Clicked cancel")

    def editStamp(self, stampItem):
        print("editing stamp")
        stamp = Stamp()
        stampObj = stamp.readStamp(stampItem)
        dlg = EditStampDlg(stampObj)
        res = dlg.exec_()
        if res == QDialog.Accepted:
            stampObj['stampDesc_text'] = dlg.eTitle.toPlainText()
            stampObj['stampNbr_text'] = dlg.eNbr.text()
            stampObj['stampValue_text'] = dlg.eValue.toPlainText()

            #print(stampObj)
            ret = dlg.getBoxInfo(dlg.pochetteList.currentItem().text())
            width = ret[0]
            stampObj['stampBox_boxWidth'] = width
            height = ret[1]
            stampObj['stampBox_boxHeight'] = height
            stampObj['pixmapItem_image'] = dlg.photo.pixmap()
            stamp.updateStamp(stampItem, stampObj)
            print("Clicked ok")


    def printPagePDF(self):
        print("Print page to PDF")

        # first unselect all objects
        for item in self.items():
            item.setSelected(False)

        printer = QPrinter(QPrinter.HighResolution)

        printer.setPageSize(QtGui.QPagedPaintDevice.A4)


        if self.pageType == "portrait":
            printer.setPageOrientation(0)
        else:
            printer.setPageOrientation(1)

        printer.setOutputFormat(QPrinter.PdfFormat)

        # TODO select the file to print
        printer.setOutputFileName("album.pdf")
        scale = printer.resolution() / 96.0

        printer.setPageMargins(0, 0, 0, 0, QPrinter.Unit.Millimeter)

        p = QPainter(printer)

        source = QtCore.QRectF(0, 0, self.width(), self.height())
        target = QRectF(0, 0, source.size().width() * scale, source.size().height() * scale)

        self.render(p, target, source)
        p.end()

    # does the print preview
    def printPreview(self):
        print("Print preview")
        previewDialog = QPrintPreviewDialog()

        previewDialog.printer().setResolution(QPrinter.HighResolution)
        previewDialog.printer().setOutputFormat(QPrinter.PdfFormat)
        previewDialog.printer().setPageSize(QtGui.QPagedPaintDevice.A4)
        if self.pageType == "portrait":
            previewDialog.printer().setPageOrientation(0)
        else:
            previewDialog.printer().setPageOrientation(1)

        previewDialog.paintRequested.connect(self.createPreview)
        previewDialog.exec_()

    # called by the print preview
    def createPreview(self, printer):
        # first unselect all objects
        for item in self.items():
            item.setSelected(False)

        scale = printer.resolution() / 96.0
        printer.setPageMargins(0, 0, 0, 0, QPrinter.Unit.Millimeter)

        p = QPainter(printer)

        source = QtCore.QRectF(0, 0, self.width(), self.height())
        target = QRectF(0, 0, source.size().width() * scale, source.size().height() * scale)

        self.render(p, target, source)

        p.end()

    # need to implement
    def printPage(self):
        print("Print page")

    # not sure that it is in use
    def drawGid(self):
        print("draw grid")
        pixmap = QPixmap(10, 10)
        painter = QPainter()

        pixmap.fill(Qt.transparent)
        painter.begin(pixmap)
        painter.setPen(Qt.gray)
        painter.drawLine(0, 0, 10, 0)
        painter.drawLine(0, 0, 0, 10)
        return pixmap

    def groupItem(self):
        sceneItems = self.items()
        for items in sceneItems:
            items.setSelected(True)

        group = self.createItemGroup(sceneItems)
        group.setFlags(QGraphicsItemGroup.ItemIsMovable | QGraphicsItemGroup.ItemIsSelectable)

    # create a new stamp
    def newStamp(self,lastStampObj):
        print("New Stamp")
        dlg = StampDlg(lastStampObj, self)
        res = dlg.exec_()
        if res == QDialog.Accepted:
            print("Clicked Done")
            # print(dlg.eYear.text())
            # stampDesc = dlg.eStampDescription.toPlainText()
            # print(dlg.eStampDescription2.toPlainText())
            # stampValue = dlg.eValue.text()
            # pixmap = ""
            # if dlg.fullPhotoPath is not None:
            #     pixmap = dlg.fullPhotoPath
            #
            # print(dlg.pochetteList.currentItem().text())
            # ret = dlg.getBoxInfo(dlg.pochetteList.currentItem().text())
            # width = ret[0]
            # height = ret[1]

            #stampNbr = dlg.stampNbrList.model().item(0, 0).text()
            stampNbr = dlg.currentStampNbr
            #
            # stamp = Stamp()
            # stamp.createStamp(self, str(stampNbr), str(stampValue), str(stampDesc),
            #                   float(width), float(height), float(0), float(0), pixmap)
            lastStampObj['year'] = dlg.eYear.text()
            lastStampObj['type'] = dlg.stampTypeCombo.currentText()
            lastStampObj['country'] = dlg.currentCountry
            lastStampObj['nbr'] = stampNbr

            return lastStampObj
        # if res == QDialog.Rejected:
        #     print("Clicked cancel")

    # Add some text
    def newLabel(self):
        print("Create new label")
        dlg = TextDlg()
        res = dlg.exec_()

        if res == QDialog.Accepted:
            print("Clicked ok")
            text = dlg.eTXT.toPlainText()
            font = dlg.eTXT.font()
            self.addTextLabel(text, 50,50, font)

        if res == QDialog.Rejected:
            print("Clicked cancel")

    # create a new copy right and add it at the bottom right of the page
    def newCopyRight(self):
        print("Create new copyright")
        text = "CopyRight © Boris du Reau 2022"
        font = QFont()
        font.setPointSize(8)
        self.addTextLabel(text, 565, 1045, font)

    def alignTop(self):
        print("")
        topY = 0.0
        if self.countSelectedItems() > 1:
            for it in self.items():
                if topY == 0 and it.isSelected() and it.parentItem() is None:
                    topY = it.y()
                if it.y() < topY and it.isSelected() and it.parentItem() is None:
                    topY = it.y()

            for it2 in self.items():
                if it2.isSelected() and it2.isSelected() and it2.parentItem() is None:
                    it2.setPos(it2.x(), topY)
        else:
            print("More than 1 item need to be selected fo aligning object")

    def alignBottom(self):
        print("")
        topY = 0.0
        if self.countSelectedItems() > 1:
            for it in self.items():
                print("it.y()%f" % it.y())
                if it.y() > topY and it.isSelected() and it.parentItem() is None:
                    topY = it.y()
            print(topY)
            for it2 in self.items():
                if it2.isSelected() and it2.parentItem() is None:
                    it2.setPos(it2.x(), topY)
        else:
            print("More than 1 item need to be selected fo aligning object")

    def alignLeft(self):
        print("")
        topX = 0.0
        if self.countSelectedItems() > 1:
            for it in self.items():
                print("it.x()%f" % it.x())
                if topX == 0:
                    topX = it.x()
                if it.x() < topX and it.isSelected() and it.parentItem() is None:
                    topX = it.x()
            print(topX)
            for it2 in self.items():
                if it2.isSelected() and it2.parentItem() is None:
                    it2.setPos(topX, it2.y())
        else:
            print("More than 1 item need to be selected fo aligning object")

    def alignRight(self):
        print("")
        topX = 0.0
        if self.countSelectedItems() > 1:
            for it in self.items():
                if it.x() > topX and it.isSelected() and it.parentItem() is None:
                    topX = it.x()
            for it2 in self.items():
                if it2.isSelected() and it2.parentItem() is None:
                    it2.setPos(topX, it2.y())
        else:
            print("More than 1 item need to be selected fo aligning object")

    def distributeHorizontally(self):
        print("")
        itemLength = 0
        minX = 0
        maxX = 0
        nbrItems = 0
        posX = []
        if self.countSelectedItems() > 2:
            for it in self.items():
                print("it.x()%f" % it.x())
                if it.isSelected() and it.parentItem() is None:
                    nbrItems = nbrItems + 1
                    if minX == 0:
                        minX = it.x()
                    if it.x() < minX:
                        minX = it.x()
                    if (it.x() + it.boundingRect().size().width()) > maxX:
                        maxX = it.x() + it.boundingRect().size().width()

                    posX.append(it.x())
                    # calculate the total length
                    itemLength = itemLength + it.boundingRect().size().width()

            space = (maxX - minX - itemLength)/(nbrItems - 1)
            posX.sort()
            print(posX)
            nextX = minX
            for px in posX:
                for i in self.items():
                    if i.isSelected() and i.parentItem() is None and px == i.x():
                        i.setPos(nextX, i.y())
                        nextX = nextX + i.boundingRect().size().width()+space

        else:
            print("More than 1 item need to be selected fo aligning object")

    # distribute all objects verticlly
    def distributeVertically(self):
        print("")
        itemLength = 0
        minY = 0
        maxY = 0
        nbrItems = 0
        posY = []
        if self.countSelectedItems() > 2:
            for it in self.items():
                print("it.x()%f" % it.y())
                if it.isSelected() and it.parentItem() is None:
                    nbrItems = nbrItems + 1
                    if minY == 0:
                        minY = it.y()
                    if it.y() < minY:
                        minY = it.y()
                    if (it.y() + it.boundingRect().size().height()) > maxY:
                        maxY = it.y() + it.boundingRect().size().height()

                    posY.append(it.y())
                    # calculate the total length
                    itemLength = itemLength + it.boundingRect().size().height()

            space = (maxY - minY - itemLength)/(nbrItems - 1)
            posY.sort()
            print(posY)
            nextY = minY
            for py in posY:
                for i in self.items():
                    if i.isSelected() and i.parentItem() is None and py == i.y():
                        i.setPos(i.x(), nextY)
                        nextY = nextY + i.boundingRect().size().height()+space
        else:
            print("More than 1 item need to be selected fo aligning object")

    # center all objects horizontally
    def centerHorizontally(self):
        print("")
        if self.countSelectedItems() > 0:
            for it in self.items():
                if it.isSelected() and it.parentItem() is None:
                    print("")
                    centerPage = self.sceneRect().width()/2
                    centerItem = it.boundingRect().width()/2
                    it.setPos(centerPage - centerItem, it.y())

    # center all objects vertically
    def centerVertically(self):
        print("")
        if self.countSelectedItems() > 0:
            for it in self.items():
                if it.isSelected() and it.parentItem() is None:
                    print("")
                    centerPage = self.sceneRect().height()/2
                    centerItem = it.boundingRect().height()/2
                    it.setPos(it.x(), centerPage - centerItem)

    def countSelectedItems(self):
        selected = 0
        for it in self.items():
            if it.isSelected():
                selected = selected+1

        return selected

    def addImage(self, fileName):
        print("add image")


        if fileName:
            print(fileName)
            pixmap = QPixmap(fileName)
            pixmapitem = QGraphicsPixmapItem(pixmap)
            pixmapitem.setFlags(QGraphicsTextItem.ItemIsMovable | QGraphicsTextItem.ItemIsSelectable
                                )
            self.addItem(pixmapitem)

        else:
            return


    def mouseDoubleClickEvent(self, event):
        print("mouse move double clicked on page")