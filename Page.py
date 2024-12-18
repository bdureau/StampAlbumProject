
from PyQt6.QtCore import QPointF, Qt, QRectF, QMarginsF
from PyQt6 import QtCore, QtGui, QtPrintSupport
from PyQt6.QtWidgets import (
    QGraphicsRectItem, QGraphicsScene, QGraphicsView, QApplication,
    QLabel, QMainWindow, QMenuBar, QMenu, QToolBar,
    QGraphicsTextItem, QGraphicsItemGroup,
    QGraphicsPixmapItem, QDialog, QLineEdit, QPushButton, QFormLayout, QFileDialog
    )
from PyQt6.QtGui import QBrush, QPainter, QPen, QPixmap, QPolygonF, QFont, QTextCursor, QAction, QTextBlockFormat, \
    QPageLayout, QPageSize
from PyQt6.QtPrintSupport import QPrintPreviewDialog, QPrinter, QPrintDialog
from StampDlg import StampDlg
from TextDlg import TextDlg
from Stamp import Stamp
from EditStampDlg import EditStampDlg


import gettext
gettext.find("PageDlg")
translate = gettext.translation('PageDlg', localedir='locale', languages=['fr'])
translate.install()
_ = translate.gettext

import configparser


class Page(QGraphicsScene):
    def __init__(self, pageType = "portrait", border=None, parent=None):
        super(Page, self).__init__(parent)
        self.pageType = pageType
        if self.pageType == "portrait":
            self.setSceneRect(0, 0, 210 / (25.4 / 96), 297 / (25.4 / 96))
            if border is not None and border:
                self.addBorder(177 / (25.4 / 96.0),
                           272 / (25.4 / 96.0),
                           19 / (25.4 / 96.0),
                           0,
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

        self.gridOn = False

    def getPageName(self):
        #self.backgroundBrush().texture().detach()
        return ""

    def addBorder(self, boxWidth, boxHeight, margin_left, margin_right, margin_top, margin_bottom):
        borderBox = QGraphicsRectItem(0, 0, boxWidth, boxHeight)
        boxPen = QPen()
        boxPen.setColor(Qt.GlobalColor.black)
        boxPen.setWidth(1)
        borderBox.setPen(boxPen)
        borderBox.setData(1, boxWidth)
        borderBox.setData(2, boxHeight)
        borderBox.setData(3, margin_left)

        borderBox2 = QGraphicsRectItem(0, 0, boxWidth - 4 - 6, (boxHeight-4-6))
        boxPen2 = QPen()
        boxPen2.setColor(Qt.GlobalColor.black)
        boxPen2.setWidth(4)
        borderBox2.setPen(boxPen2)
        borderBox2.setData(1, boxWidth - 4 - 6)
        borderBox2.setData(2, boxHeight - 4 - 6)
        borderBox2.setData(3, margin_left)

        borderBox3 = QGraphicsRectItem(0, 0, boxWidth - 4 - 6 - 9, (boxHeight - 4 - 6 - 9))
        boxPen3 = QPen()
        boxPen3.setColor(Qt.GlobalColor.black)
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

    def addTextLabel(self, text, x=20, y=20, font=None, align=Qt.AlignmentFlag.AlignCenter, labelType ="textLabel"):

        textLabel = QGraphicsTextItem(text)
        textLabel.setData(0, "textLabel")

        if font is not None:
            textLabel.setFont(font)
        textLabel.setTextWidth(textLabel.boundingRect().size().width())

        cursor = textLabel.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        format = QTextBlockFormat()
        format.setAlignment(align)
        cursor.mergeBlockFormat(format)
        cursor.clearSelection()
        textLabel.setTextCursor(cursor)


        textLabel.setPos(x, y)
        textLabel.setFlags(QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable |
                           QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable)
        textLabel.setData(0, labelType)

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

        itemType = 0
        for item in items:

            itemType = item.type().real

            if itemType == 10:
                # This is a stamp
                self.editStamp(item)
            elif itemType == 8:
                # This is a text label
                self.editLabel(item)

    def printObjectDebugInfo(self):
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

        itemType = 0
        for item in items:
            itemType = item.type().real

            if itemType == 10:
                # This is a stamp
                print(item.data(0))
                #self.editStamp(item)
                print("stamp")
                print(item.pos().x())
                print(item.pos().y())
                print("X")
                print(item.x())
                print(item.y())

            elif itemType == 8:
                # This is a text label
                #self.editLabel(item)
                print("text label")

    def editLabel(self, item):

        dlg = TextDlg(item)
        res = dlg.exec()
        print("edit label")
        #accepted
        if res == 1:
            text = dlg.eTXT.toPlainText()

            font = dlg.eTXT.font()
            item.setPlainText(text)
            item.setFont(font)
            # dummy text label to calculate the size correctly
            textLabel = QGraphicsTextItem(text)
            textLabel.setFont(font)

            item.setTextWidth(textLabel.boundingRect().size().width())
            print("edit format")
            cursor = item.textCursor()
            cursor.select(QTextCursor.SelectionType.Document)
            format = QTextBlockFormat()

            align = dlg.eTXT.alignment()
            if align == Qt.AlignmentFlag.AlignLeft:
                print("Qt.AlignLeft")
            if align == Qt.AlignmentFlag.AlignRight:
                print("Qt.AlignRight")
            if align == Qt.AlignmentFlag.AlignCenter:
                print("Qt.AlignCenter")
            print(align)
            format.setAlignment(align)
            cursor.mergeBlockFormat(format)
            cursor.clearSelection()
            item.setTextCursor(cursor)

            item.setFlags(QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable |
                          QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable)


        #rejected
        if res == 0:
            print("Clicked cancel")

    def editStamp(self, stampItem):
        stamp = Stamp()
        stampObj = stamp.readStamp(stampItem)
        dlg = EditStampDlg(stampObj)
        res = dlg.exec()
        # accepted
        if res == 1:
            stampObj['stampDesc_text'] = dlg.eTitle.toPlainText()
            stampObj['stampNbr_text'] = dlg.eNbr.text()
            stampObj['stampValue_text'] = dlg.eValue.toPlainText()

            ret = dlg.getBoxInfo(dlg.pochetteList.currentItem().text())
            width = ret[0]
            stampObj['stampBox_boxWidth'] = width
            height = ret[1]
            stampObj['stampBox_boxHeight'] = height
            stampObj['pixmapItem_image'] = dlg.photo.pixmap()
            print("update stamp")
            stamp.updateStamp(stampItem, stampObj, self)

    def printPagePDF(self,fileName2):
        print("printPagePDF")
        # first unselect all objects
        for item in self.items():
            item.setSelected(False)

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)

        #printer.setPageSize(QtGui.QPagedPaintDevice.A4)

        if self.pageType == "portrait":
            printer.setPageOrientation(QPageLayout.Orientation.Portrait)
        else:
            printer.setPageOrientation(QPageLayout.Orientation.Landscape)

        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(fileName2)
        scale = printer.resolution() / 96.0

        printer.setPageMargins(QtCore.QMarginsF(0.0, 0.0, 0.0, 0.0), QtGui.QPageLayout.Unit.Millimeter)

        p = QPainter(printer)

        source = QtCore.QRectF(0, 0, self.width(), self.height())
        target = QRectF(0, 0, source.size().width() * scale, source.size().height() * scale)

        self.render(p, target, source)
        p.end()

    # does the print preview
    def printPreview(self):
        print("Print preview")
        previewDialog = QPrintPreviewDialog()

        previewDialog.printer().setResolution(QPrinter.PrinterMode.HighResolution.value)

        previewDialog.printer().setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        #previewDialog.printer().setPageSize(QtGui.QPagedPaintDevice.A4)
        if self.pageType == "portrait":
            previewDialog.printer().setPageOrientation(QPageLayout.Orientation.Portrait)
        else:
            previewDialog.printer().setPageOrientation(QPageLayout.Orientation.Landscape)

        previewDialog.paintRequested.connect(self.createPreview)
        previewDialog.exec()

    # called by the print preview
    def createPreview(self, printer):
        # first unselect all objects
        for item in self.items():
            item.setSelected(False)

        scale = printer.resolution() / 96.0

        printer.setPageMargins(QtCore.QMarginsF(0.0, 0.0, 0.0, 0.0), QtGui.QPageLayout.Unit.Millimeter)

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

        pixmap.fill(Qt.GlobalColor.transparent)
        painter.begin(pixmap)
        painter.setPen(Qt.GlobalColor.gray)
        painter.drawLine(0, 0, 10, 0)
        painter.drawLine(0, 0, 0, 10)
        return pixmap

    def groupItem(self):
        sceneItems = self.items()
        for items in sceneItems:
            items.setSelected(True)

        group = self.createItemGroup(sceneItems)
        group.setFlags(QGraphicsItemGroup.GraphicsItemFlag.ItemIsMovable | QGraphicsItemGroup.GraphicsItemFlag.ItemIsSelectable)

    # create a new stamp
    def newStamp(self, lastStampObj):
        print("New Stamp")
        dlg = StampDlg(lastStampObj, self)
        res = dlg.exec()

        #accepted
        if res == 1:
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
        textLabel = QGraphicsTextItem("")
        textLabelFont = textLabel.font()
        textLabelFont.setPointSize(10)
        textLabel.setFont(textLabelFont)

        dlg = TextDlg(textLabel)
        res = dlg.exec()

        print(res)
        #accepted
        if res == 1:
            print("Clicked ok")
            text = dlg.eTXT.toPlainText()
            font = dlg.eTXT.font()
            align = dlg.eTXT.alignment()

            self.addTextLabel(text, 50, 50, font, align)

        #rejected
        if res == 0:
            print("Clicked cancel")

    # create a new copyright and add it at the bottom right of the page
    def newCopyRight(self):
        text = "CopyRight © Boris du Reau 2003-2023"
        #get it from config
        configParser = configparser.RawConfigParser()
        configFilePath = r'stamp_album.cfg'
        configParser.read(configFilePath)
        if configParser.has_section('CONF'):
            conf = configParser['CONF']
            if configParser.has_option('CONF', 'copyright'):
                text = conf['copyright']

        font = QFont()
        font.setPointSize(6)
        if self.pageType == "portrait":
            self.addTextLabel(text, 80, 1045, font, Qt.AlignmentFlag.AlignLeft, "labelCopyRight")
        else:
            self.addTextLabel(text, 60, 710, font, Qt.AlignmentFlag.AlignLeft, "labelCopyRight")

    def newPageNbr(self):
        print("Create new  nbr")
        textLabel = QGraphicsTextItem("")
        textLabelFont = textLabel.font()
        textLabelFont.setPointSize(8)
        textLabel.setFont(textLabelFont)

        dlg = TextDlg(textLabel)
        #dlg = TextDlg()
        res = dlg.exec()

        # accepted
        if res == 1:
            print("Clicked ok")
            text = dlg.eTXT.toPlainText()
            font = dlg.eTXT.font()
            align = dlg.eTXT.alignment()

            self.addPageNbr(text, font, align)
        # rejected
        if res == 0:
            print("Clicked cancel")

    def addPageNbr(self, pageName, font, align=Qt.AlignmentFlag.AlignLeft):
        print("new page number")
        #font = QFont()
        #font.setPointSize(8)
        textLabel = QGraphicsTextItem(pageName)
        textLabel.setFont(font)
        textWidth = textLabel.boundingRect().size().width()
        if self.pageType == "portrait":
            self.addTextLabel(pageName, (210 / (25.4 / 96)) - 60 - textWidth, 1045, font, align, "labelPageNbr")
        else:
            self.addTextLabel(pageName, (297 / (25.4 / 96)) - 60 - textWidth, 710, font, align, "labelPageNbr")

    def addPageYear(self):
        textLabel = QGraphicsTextItem("")
        textLabelFont = textLabel.font()
        textLabelFont.setPointSize(10)
        textLabelFont.setBold(True)
        textLabel.setFont(textLabelFont)

        dlg = TextDlg(textLabel)
        res = dlg.exec()

        # accepted
        if res == 1:
            print("Clicked ok")
            text = dlg.eTXT.toPlainText()
            font = dlg.eTXT.font()
            align = dlg.eTXT.alignment()

            self.addYear(text, font, align)
        # rejected
        if res == 0:
            print("Clicked cancel")

    def addYear(self, year, font, align):
        print("add year")

        textLabel = QGraphicsTextItem(year)
        textLabel.setFont(font)
        textWidth = textLabel.boundingRect().size().width()
        if self.pageType == "portrait":
            self.addTextLabel(year, ((210 / (25.4 / 96) - textWidth))/2, 80, font, align, "labelYear")
        else:
            self.addTextLabel(year, ((297 / (25.4 / 96) - textWidth)) / 2, 80, font, Qt.AlignmentFlag.AlignLeft,
                              "labelYear")

    def alignTop(self):
        print("alignTop")
        topY = 0.0
        if self.countSelectedItems() > 1:
            for it in self.items():
                if topY == 0.0 and it.isSelected() and it.parentItem() is None:
                    topY = it.y()
                if it.y() < topY and it.isSelected() and it.parentItem() is None:
                    topY = it.y()

            for it2 in self.items():
                if it2.isSelected() and it2.isSelected() and it2.parentItem() is None:
                    it2.setPos(it2.x(), topY)
        else:
            print("More than 1 item need to be selected fo aligning object")

    def alignBottom(self):
        print("align bottom")
        topY = 0.0
        if self.countSelectedItems() > 1:
            for it in self.items():
                if (it.y() + it.boundingRect().size().height()) > topY and it.isSelected() and it.parentItem() is None:
                    topY = it.y() + it.boundingRect().size().height()

            for it2 in self.items():
                if it2.isSelected() and it2.parentItem() is None:
                    it2.setPos(it2.x(), topY - it2.boundingRect().height())
        else:
            print("More than 1 item need to be selected fo aligning object")

    def alignLeft(self):
        print("alignLeft")
        topX = self.sceneRect().width()
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
        print("alignRight")
        topX = 0.0
        if self.countSelectedItems() > 1:
            for it in self.items():
                if (it.x() + it.boundingRect().size().width()) > topX and it.isSelected() and it.parentItem() is None:
                    topX = (it.x() + it.boundingRect().size().width())
            for it2 in self.items():
                if it2.isSelected() and it2.parentItem() is None:
                    it2.setPos(topX - it2.boundingRect().size().width(), it2.y())
        else:
            print("More than 1 item need to be selected fo aligning object")

    def distributeHorizontally(self):
        #review!!!!
        print("distributeHorizontally")
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
                    if it.type().real == 8:
                        if minX == 0:
                            minX = it.x()
                        if it.x() < minX:
                            minX = it.x()
                        if (it.x() + it.boundingRect().size().width()) > maxX:
                            maxX = it.x() + it.boundingRect().size().width()
                    elif it.type().real == 10 and it.data(0) == "stampGroup":
                        stampIts = it.childItems()
                        for stampIt in stampIts:
                            if stampIt.type().real == 3:
                                if stampIt.x() < 0:
                                    if minX == 0:
                                        minX = it.x() + stampIt.x()
                                    if (it.x() - stampIt.x()) < minX:
                                        minX = it.x() + stampIt.x()
                                    if (it.x() + stampIt.x() + it.boundingRect().size().width()) > maxX:
                                        maxX = it.x() + it.boundingRect().size().width()
                                else:
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
                        if i.type().real == 8:
                            nextX = nextX + i.boundingRect().size().width()+space
                        elif i.type().real == 10 and i.data(0) == "stampGroup":
                            stampItems = i.childItems()
                            for stampItem in stampItems:
                                if stampItem.type().real == 3:
                                    if stampItem.x() < 0:
                                        nextX = nextX + i.boundingRect().size().width() + space
                                    else:
                                        nextX = nextX + i.boundingRect().size().width() + space


        else:
            print("More than 1 item need to be selected fo aligning object")

    # distribute all objects verticlly
    def distributeVertically(self):
        print("distributeVertically")
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
        print("centerHorizontally")
        if self.countSelectedItems() > 0:
            for it in self.items():
                if it.isSelected() and it.parentItem() is None:
                    print(it.type().real)
                    centerPage = self.sceneRect().width()/2
                    print("centerPage:")
                    print(centerPage)
                    if it.type().real == 8:
                        centerItem = it.boundingRect().width()/2
                        print("centerItem:")
                        print(centerItem)
                        it.setPos((centerPage - centerItem), it.y())
                        print("center")
                        print(centerPage - centerItem)
                    elif it.type().real == 10 and it.data(0) == "stampGroup":
                        print("stamp")
                        stampItems = it.childItems()
                        for stampItem in stampItems:
                            if stampItem.type().real == 3:
                                print("stampBox")
                                if stampItem.x() < 0:
                                    centerItem = (it.boundingRect().width() / 2) + stampItem.x()
                                    it.setPos((centerPage - centerItem), it.y())
                                else:
                                    centerItem = it.boundingRect().width() / 2
                                    it.setPos((centerPage - centerItem), it.y())


    # center all objects vertically
    def centerVertically(self):
        print("centerVertically")
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
            pixmapitem.setFlags(QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable |
                                QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable)
            self.addItem(pixmapitem)
        else:
            return

    def mouseDoubleClickEvent(self, event):
        print("mouse move double clicked on page")
