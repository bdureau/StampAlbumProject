"""
Page Module
-----------
Manages the graphics scene for custom stamp album pages including items,
decorations, borders, rich text items, undo stack history, and print preview.

Author: Boris du Reau
"""
import configparser
from pathlib import Path
import gettext
from ResizablePixmapItem import ResizablePixmapItem  # Import du composant
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
import configparser
from pathlib import Path
from PageBorder import PageBorder
import gettext
from PyQt6.QtWidgets import QGraphicsScene
from PyQt6.QtGui import QUndoStack
from UndoCommands import AddItemCommand, DeleteItemsCommand, MoveCommand

gettext.find("PageDlg")
translate = gettext.translation('PageDlg', localedir='locale', languages=['fr'])
translate.install()
_ = translate.gettext



class Page(QGraphicsScene):
    """Custom QGraphicsScene representing a single stamp album page."""
    def __init__(self, pageType = "portrait", border=None, parent=None):
        super(Page, self).__init__(parent)
        self.pageType = pageType

        # Undo/Redo history stack for the current page scene
        self.undoStack = QUndoStack(self)
        self.mouse_press_positions = {}

        style = self.get_configured_border_style()
        if self.pageType == "portrait":
            self.setSceneRect(0, 0, 210 / (25.4 / 96), 297 / (25.4 / 96))
            if border is not None and border:
                self.addBorder(177 / (25.4 / 96.0),
                           272 / (25.4 / 96.0),
                           19 / (25.4 / 96.0),
                           0,
                           0,
                           0,style)
        else:
            self.setSceneRect(0, 0, 297 / (25.4 / 96), 210 / (25.4 / 96))
            if border is not None and border:
                self.addBorder(272 / (25.4 / 96.0),
                           177 / (25.4 / 96.0),
                           ((297-272) / 2) / (25.4 / 96.0),
                           0,
                           19 / (25.4 / 96.0),
                           0,style)

        self.gridOn = False

    def addItemNative(self, item):
        """Add item directly to scene without pushing an Undo command."""
        if item.scene() != self:
            super().addItem(item)

    def removeItemNative(self, item):
        """Suppression directe de la scène sans ajouter de commande dans l'historique."""
        if item.scene() == self:
            super().removeItem(item)

    def addItemWithUndo(self, item, text="Add Item"):
        """Remove item directly from scene without pushing an Undo command."""
        if item.parentItem() is None:
            cmd = AddItemCommand(self, item, text)
            self.undoStack.push(cmd)  # Push appelle automatiquement cmd.redo() une fois !
        else:
            self.addItemNative(item)

    def addItem(self, item):
        """Override addItem to automatically register undo history."""
        super().addItem(item)
        # N'enregistre que les objets principaux (pas les enfants de groupes)
        if item.parentItem() is None:
            #cmd = AddItemCommand(self, item)
            cmd = AddItemCommand(self, item, _("Add Item"))
            self.undoStack.push(cmd)

    def removeItems(self):
        """Remove selected top-level items and record operation in Undo stack."""
        #items = self.selectedItems()
        items = [it for it in self.selectedItems() if it.parentItem() is None]
        if items:
            cmd = DeleteItemsCommand(self, items)
            self.undoStack.push(cmd)

    def getPageName(self):
        return ""

    def get_configured_border_style(self) -> str:
        """Read default border style from configuration file."""
        config_path = Path(__file__).resolve().parent / 'stamp_album.cfg'
        if config_path.exists():
            parser = configparser.RawConfigParser()
            parser.read(config_path)
            if parser.has_option('CONF', 'type encadrement'):
                return parser.get('CONF', 'type encadrement')
        return PageBorder.STYLE_TRIPLE

    def addBorder(self, boxWidth, boxHeight, margin_left, margin_right, margin_top, margin_bottom,style=None):
        """Add a decorative border to the page using PageBorder class."""
        if not style:
            style = PageBorder.STYLE_TRIPLE  # Style par défaut : Triple (Classic)

        border = PageBorder(boxWidth, boxHeight, style=style)

        if margin_top != 0:
            margin_top2 = margin_top
        else:
            margin_top2 = (self.height() - border.boundingRect().size().height()) / 2

        border.setPos(margin_left, margin_top2)
        self.addItem(border)

    def addTextLabel(self, text, x=20, y=20, font=None, align=Qt.AlignmentFlag.AlignCenter, labelType ="textLabel"):
        """Add a text label to the page with alignment and font attributes."""
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

        self.addItemWithUndo(textLabel, _("Add Text"))

    def addRichText(self, html_content="", x=50, y=50, label_type="richTextLabel"):
        """
        Add a rich-text block supporting HTML content, character-level styling,
        font family, sizes, colors, and paragraph alignments.
        """
        text_item = QGraphicsTextItem()
        text_item.setData(0, label_type)

        if html_content:
            text_item.setHtml(html_content)
        else:
            text_item.setHtml(
                "<p style='font-family:Sans-Serif; font-size:12pt;'>Double-click to edit rich text...</p>")

        text_item.setTextWidth(200)
        text_item.setPos(x, y)
        text_item.setFlags(
            QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable
        )

        if hasattr(self, 'addItemWithUndo'):
            self.addItemWithUndo(text_item, _("Add Rich Text"))
        else:
            self.addItem(text_item)

        return text_item

    def editRichText(self, item):
        """Open the rich text dialog editor for an existing text block."""
        try:
            from RichTextDlg import RichTextDlg
            dlg = RichTextDlg(item)
            if dlg.exec() == 1:  # Accepted
                item.setHtml(dlg.get_html())
        except Exception as e:
            print(f"Error editing rich text: {e}")

    def clearPage(self):
        """Remove all items from the current page."""
        items = self.items()
        for item in items:
            self.removeItem(item)

    #is it still in use?
    def removeItems(self):
        items = self.selectedItems()
        for item in items:
            self.removeItem(item)

    def editObject(self):
        """Edit currently selected scene item safely."""
        items = self.selectedItems()
        if len(items) != 1:
            return

        selected_item = items[0]

        # Resolve to top-level parent item if a child item within a group was clicked
        if selected_item.parentItem() is not None:
            top_item = selected_item.parentItem()
            while top_item.parentItem() is not None:
                top_item = top_item.parentItem()
        else:
            top_item = selected_item

        try:
            # 1. Rich Text Item
            if top_item.data(0) == "richTextLabel":
                self.editRichText(top_item)

            # 2. Standard Text Item (using direct class check)
            elif isinstance(top_item, QGraphicsTextItem) or top_item.type().real == 8:
                self.editLabel(top_item)

            # 3. Stamp Group Item
            elif top_item.data(0) == "stampGroup" or top_item.type().real == 10:
                self.editStamp(top_item)

        except Exception as e:
            print(f"Error during item editing: {e}")

    def printObjectDebugInfo(self):
        """Print debug information for selected scene items."""
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
                print("text label")

    def editLabel(self, item):
        """Edit a standard text item using TextDlg."""
        dlg = TextDlg(item)
        res = dlg.exec()
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
        """Edit stamp group attributes using EditStampDlg."""
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

            stamp.updateStamp(stampItem, stampObj, self)

    def printPagePDF(self,fileName2):
        """Export current page as a PDF file."""
        # first unselect all objects
        for item in self.items():
            item.setSelected(False)

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)

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
        """Display print preview for the current page."""
        previewDialog = QPrintPreviewDialog()
        previewDialog.printer().setResolution(QPrinter.PrinterMode.HighResolution.value)
        previewDialog.printer().setOutputFormat(QPrinter.OutputFormat.PdfFormat)

        if self.pageType == "portrait":
            previewDialog.printer().setPageOrientation(QPageLayout.Orientation.Portrait)
        else:
            previewDialog.printer().setPageOrientation(QPageLayout.Orientation.Landscape)

        previewDialog.paintRequested.connect(self.createPreview)
        previewDialog.exec()

    # called by the print preview
    def createPreview(self, printer):
        """Render scene page preview for QPrintPreviewDialog."""
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

    #is it still in use?
    def groupItem(self):
        sceneItems = self.items()
        for items in sceneItems:
            items.setSelected(True)

        group = self.createItemGroup(sceneItems)
        group.setFlags(QGraphicsItemGroup.GraphicsItemFlag.ItemIsMovable | QGraphicsItemGroup.GraphicsItemFlag.ItemIsSelectable)

    # create a new stamp
    def newStamp(self, lastStampObj):
        """Create and place a new stamp item from StampDlg."""
        dlg = StampDlg(lastStampObj, self)
        res = dlg.exec()

        #accepted
        if res == 1:
            stampNbr = dlg.currentStampNbr
            lastStampObj['year'] = dlg.eYear.text()
            lastStampObj['type'] = dlg.stampTypeCombo.currentText()
            lastStampObj['country'] = dlg.currentCountry
            lastStampObj['nbr'] = stampNbr

            return lastStampObj

    # Add some text
    def newLabel(self):
        """Prompt user for text and place a standard label."""
        textLabel = QGraphicsTextItem("")
        textLabelFont = textLabel.font()
        textLabelFont.setPointSize(10)
        textLabel.setFont(textLabelFont)

        dlg = TextDlg(textLabel)
        res = dlg.exec()

        #accepted
        if res == 1:
            text = dlg.eTXT.toPlainText()
            font = dlg.eTXT.font()
            align = dlg.eTXT.alignment()
            self.addTextLabel(text, 50, 50, font, align)

    # create a new copyright and add it at the bottom right of the page
    def newCopyRight(self):
        """Add a copyright footer to the page."""
        text = "CopyRight © Boris du Reau 2003-2026"
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
        """Prompt user and create a page number label."""
        textLabel = QGraphicsTextItem("")
        textLabelFont = textLabel.font()
        textLabelFont.setPointSize(8)
        textLabel.setFont(textLabelFont)

        dlg = TextDlg(textLabel)
        res = dlg.exec()

        # accepted
        if res == 1:
            text = dlg.eTXT.toPlainText()
            font = dlg.eTXT.font()
            align = dlg.eTXT.alignment()
            self.addPageNbr(text, font, align)

    def addPageNbr(self, pageName, font, align=Qt.AlignmentFlag.AlignLeft):
        """Position page number label at the bottom right of the page."""
        textLabel = QGraphicsTextItem(pageName)
        textLabel.setFont(font)
        textWidth = textLabel.boundingRect().size().width()
        if self.pageType == "portrait":
            self.addTextLabel(pageName, (210 / (25.4 / 96)) - 60 - textWidth, 1045, font, align, "labelPageNbr")
        else:
            self.addTextLabel(pageName, (297 / (25.4 / 96)) - 60 - textWidth, 710, font, align, "labelPageNbr")

    def addPageYear(self):
        """Prompt user for year and place a header year label."""
        textLabel = QGraphicsTextItem("")
        textLabelFont = textLabel.font()
        textLabelFont.setPointSize(10)
        textLabelFont.setBold(True)
        textLabel.setFont(textLabelFont)

        dlg = TextDlg(textLabel)
        res = dlg.exec()

        # accepted
        if res == 1:
            text = dlg.eTXT.toPlainText()
            font = dlg.eTXT.font()
            align = dlg.eTXT.alignment()
            self.addYear(text, font, align)


    def addYear(self, year, font, align):
        """Position year header label at top center of the page."""
        textLabel = QGraphicsTextItem(year)
        textLabel.setFont(font)
        textWidth = textLabel.boundingRect().size().width()
        if self.pageType == "portrait":
            self.addTextLabel(year, ((210 / (25.4 / 96) - textWidth))/2, 80, font, align, "labelYear")
        else:
            self.addTextLabel(year, ((297 / (25.4 / 96) - textWidth)) / 2, 80, font, Qt.AlignmentFlag.AlignLeft,
                              "labelYear")

    def alignTop(self):
        """Align top boundaries of selected items."""
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
        """Align bottom boundaries of selected items."""
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
        """Align left boundaries of selected items."""
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
        """Align right boundaries of selected items."""
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
        """Space selected items horizontally with equal margins."""
        itemLength = 0
        minX = 0
        maxX = 0
        nbrItems = 0
        posX = []

        if self.countSelectedItems() > 2:
            for it in self.items():
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
        """Space selected items vertically with equal margins."""
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
        """Center selected items horizontally on page."""
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
        """Center selected items vertically on page."""
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
        """Add an image to the scene with interactive resize handles."""
        if fileName:
            pixmap = QPixmap(fileName)
            if not pixmap.isNull():
                pixmapitem = ResizablePixmapItem(pixmap)
                # Positionnement initial sur la scène
                pixmapitem.setPos(50, 50)
                #self.addItemWithUndo(pixmapitem)
                self.addItem(pixmapitem)

    def mouseDoubleClickEvent(self, event):
        """Safely intercept double clicks to launch edit dialogs without triggering in-place editing."""
        item = self.itemAt(event.scenePos(), QtGui.QTransform())
        if item:
            # Resolve to top-level item if child item was clicked
            top_item = item.topLevelItem() if item.topLevelItem() else item

            # Select target item explicitly
            self.clearSelection()
            top_item.setSelected(True)

            # Trigger object edit dialog
            self.editObject()
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        """Record initial positions for items before drag operations."""
        self.mouse_press_positions = {
            item: item.pos() for item in self.selectedItems() if item.parentItem() is None
        }
        super().mousePressEvent(event)



    def mouseReleaseEvent(self, event):
        """Check for moved items on drag release and append to UndoStack."""
        super().mouseReleaseEvent(event)

        moved_items = []
        old_positions = []

        for item, old_pos in self.mouse_press_positions.items():
            # Ne crée MoveCommand que si l'élément n'était pas en cours de redimensionnement
            if hasattr(item, 'is_resizing') and item.is_resizing:
                continue

            if item.pos() != old_pos:
                moved_items.append(item)
                old_positions.append(old_pos)

        if moved_items:
            cmd = MoveCommand(moved_items, old_positions)
            self.undoStack.push(cmd)

        self.mouse_press_positions.clear()