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
from ResizablePixmapItem import ResizablePixmapItem
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
from PageBorder import PageBorder
from PyQt6.QtGui import QUndoStack
from UndoCommands import AddItemCommand, DeleteItemsCommand, MoveCommand

gettext.find("PageDlg")
translate = gettext.translation('PageDlg', localedir='locale', languages=['fr'])
translate.install()
_ = translate.gettext


class Page(QGraphicsScene):
    """Custom QGraphicsScene representing a single stamp album page."""

    def __init__(self, pageType="portrait", border=None, paper_format=None, border_style=None, parent=None):
        super(Page, self).__init__(parent)
        self.pageType = pageType

        # Set page background color to plain white
        self.setBackgroundBrush(QBrush(Qt.GlobalColor.white))

        # Undo/Redo history stack for the current page scene
        self.undoStack = QUndoStack(self)
        self.mouse_press_positions = {}

        # If paper_format is not provided, load from config (or default to A4)
        if not paper_format:
            paper_format = self.get_configured_paper_format()

        self.paper_format = paper_format

        if self.paper_format == "Letter":
            self.page_width_mm = 215.9
            self.page_height_mm = 279.4
        else:
            self.page_width_mm = 210.0
            self.page_height_mm = 297.0

        # Convert mm to pixels (dpi = 96)
        px_w = self.page_width_mm / (25.4 / 96.0)
        px_h = self.page_height_mm / (25.4 / 96.0)

        # Utilise le style passé en paramètre ou celui de la configuration
        style = border_style if border_style else self.get_configured_border_style()

        if self.pageType == "portrait":
            self.setSceneRect(0, 0, px_w, px_h)
            if border:
                border_w = (self.page_width_mm - 33.0) / (25.4 / 96.0)
                border_h = (self.page_height_mm - 25.0) / (25.4 / 96.0)
                margin_l = 19.0 / (25.4 / 96.0)
                self.addBorder(border_w, border_h, margin_l, 0, 0, 0, style)
        else:
            self.setSceneRect(0, 0, px_h, px_w)
            if border:
                border_w = (self.page_height_mm - 25.0) / (25.4 / 96.0)
                border_h = (self.page_width_mm - 33.0) / (25.4 / 96.0)
                margin_l = ((px_h - border_w) / 2.0)
                margin_t = 19.0 / (25.4 / 96.0)
                self.addBorder(border_w, border_h, margin_l, 0, margin_t, 0, style)

        self.gridOn = False

    def get_configured_paper_format(self) -> str:
        """Read default paper format from configuration file."""
        config_path = Path(__file__).resolve().parent / 'stamp_album.cfg'
        if config_path.exists():
            parser = configparser.RawConfigParser()
            parser.read(config_path)
            if parser.has_option('CONF', 'paper format'):
                return parser.get('CONF', 'paper format')
        return "A4"

    def addItemNative(self, item):
        """Add item directly to scene without pushing an Undo command."""
        if item.scene() != self:
            super().addItem(item)

    def removeItemNative(self, item):
        """Suppression directe de la scène sans ajouter de commande dans l'historique."""
        if item.scene() == self:
            super().removeItem(item)

    def addItemWithUndo(self, item, text="Add Item"):
        """Add item to scene and record in Undo stack."""
        if item.parentItem() is None:
            if item.scene() != self:
                super().addItem(item)
            cmd = AddItemCommand(self, item, text)
            self.undoStack.push(cmd)
        else:
            self.addItemNative(item)

    def addItem(self, item):
        """Override addItem to add item natively without triggering infinite recursion during setup."""
        if item.scene() != self:
            super().addItem(item)

    def removeItems(self):
        """Remove selected top-level items and record operation in Undo stack."""
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

    def addBorder(self, boxWidth, boxHeight, margin_left, margin_right, margin_top, margin_bottom, style=None):
        """Add a decorative border to the page using PageBorder class."""
        if not style:
            style = PageBorder.STYLE_TRIPLE

        border = PageBorder(boxWidth, boxHeight, style=style)

        if margin_top != 0:
            margin_top2 = margin_top
        else:
            margin_top2 = (self.height() - border.boundingRect().size().height()) / 2

        border.setPos(margin_left, margin_top2)
        self.addItem(border)

    def addTextLabel(self, text, x=20, y=20, font=None, align=Qt.AlignmentFlag.AlignCenter, labelType="textLabel"):
        """Add a text label to the page with alignment and font attributes."""
        textLabel = QGraphicsTextItem(text)
        textLabel.setData(0, labelType)

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

        # Empêche l'édition directe sur la scène pour forcer l'ouverture de la boîte de dialogue TextDlg
        textLabel.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        textLabel.setFlags(
            QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable
        )

        self.addItemWithUndo(textLabel, _("Add Text"))

    def addRichText(self, html_content="", x=50, y=50, label_type="richTextLabel"):
        """Add a rich-text block supporting HTML content."""
        text_item = QGraphicsTextItem()
        text_item.setData(0, label_type)

        if html_content:
            text_item.setHtml(html_content)
        else:
            text_item.setHtml(
                "<p style='font-family:Sans-Serif; font-size:12pt;'>Double-click to edit rich text...</p>")

        text_item.setTextWidth(200)
        text_item.setPos(x, y)

        text_item.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
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
            if dlg.exec() == 1:
                item.setHtml(dlg.get_html())
        except Exception as e:
            print(f"Error editing rich text: {e}")

    def clearPage(self):
        """Remove all items from the current page."""
        items = self.items()
        for item in items:
            self.removeItem(item)

    def removeItems(self):
        items = self.selectedItems()
        for item in items:
            self.removeItem(item)

    def editObject(self, item=None):
        """Edit currently selected scene item or the item passed directly."""
        top_item = item

        if top_item is None:
            items = self.selectedItems()
            if len(items) != 1:
                return
            top_item = items[0]
            while top_item.parentItem() is not None:
                top_item = top_item.parentItem()

        if top_item is None:
            return

        try:
            raw_data = top_item.data(0)
            data_type = str(raw_data) if raw_data is not None else ""

            print(
                f"Editing item - Class: {top_item.__class__.__name__}, Type: {top_item.type()}, Data(0): '{data_type}'")

            # EXCLURE les bordures du double-clic d'édition pour éviter le crash
            if data_type == "borderGroup":
                return

            # 2. Cas du Rich Text
            if data_type == "richTextLabel":
                self.editRichText(top_item)

            # 3. Cas du Timbre (stampGroup)
            elif data_type == "stampGroup" or top_item.type() == 10:
                self.editStamp(top_item)

            # 4. Cas de TOUS les objets texte
            elif (
                    data_type in ["textLabel", "labelPageNbr", "labelCopyRight", "labelYear"]
                    or isinstance(top_item, QGraphicsTextItem)
                    or top_item.type() == 8
            ):
                self.editLabel(top_item)
            else:
                print(f"Unrecognized item type for editing: {data_type}")

        except Exception as e:
            print(f"Error during item editing: {e}")

    def printObjectDebugInfo(self):
        """Print debug information for selected scene items."""
        items = self.selectedItems()
        nbrOfItems = len(items)

        if nbrOfItems > 1:
            print("more than one item selected")
            return

        if nbrOfItems == 0:
            print("no items selected")
            return

        for item in items:
            itemType = item.type().real
            if itemType == 10:
                print(item.data(0))
                print("stamp")
                print(item.pos().x())
                print(item.pos().y())
            elif itemType == 8:
                print("text label")

    def editLabel(self, item):
        """Edit a standard text item using TextDlg."""
        dlg = TextDlg(item)
        res = dlg.exec()
        if res == 1:
            text = dlg.eTXT.toPlainText()
            font = dlg.eTXT.font()
            item.setPlainText(text)
            item.setFont(font)
            textLabel = QGraphicsTextItem(text)
            textLabel.setFont(font)

            item.setTextWidth(textLabel.boundingRect().size().width())

            cursor = item.textCursor()
            cursor.select(QTextCursor.SelectionType.Document)
            format = QTextBlockFormat()

            align = dlg.eTXT.alignment()
            format.setAlignment(align)
            cursor.mergeBlockFormat(format)
            cursor.clearSelection()
            item.setTextCursor(cursor)

            item.setFlags(QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable |
                          QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable)

    def editStamp(self, stampItem):
        """Edit stamp group attributes using EditStampDlg."""
        stamp = Stamp()
        stampObj = stamp.readStamp(stampItem)
        dlg = EditStampDlg(stampObj)
        res = dlg.exec()
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

    def printPagePDF_old(self, fileName2):
        """Export current page as a PDF file."""
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

    def printPagePDF(self, fileName2):
        """Export current page as a PDF file."""
        # 1. Désélectionner tous les objets
        for item in self.items():
            item.setSelected(False)

        # 2. Cacher les lignes guides temporairement
        guides = [it for it in self.items() if it.data(0) == "guideLine"]
        for g in guides:
            g.hide()

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

        # 3. Réafficher les lignes guides une fois l'export terminé
        for g in guides:
            g.show()

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

    def createPreview_old(self, printer):
        """Render scene page preview for QPrintPreviewDialog."""
        for item in self.items():
            item.setSelected(False)

        scale = printer.resolution() / 96.0
        printer.setPageMargins(QtCore.QMarginsF(0.0, 0.0, 0.0, 0.0), QtGui.QPageLayout.Unit.Millimeter)

        p = QPainter(printer)
        source = QtCore.QRectF(0, 0, self.width(), self.height())
        target = QRectF(0, 0, source.size().width() * scale, source.size().height() * scale)

        self.render(p, target, source)
        p.end()

    def createPreview(self, printer):
        """Render scene page preview for QPrintPreviewDialog."""
        # 1. Désélectionner tous les objets
        for item in self.items():
            item.setSelected(False)

        # 2. Cacher les lignes guides temporairement
        guides = [it for it in self.items() if it.data(0) == "guideLine"]
        for g in guides:
            g.hide()

        scale = printer.resolution() / 96.0
        printer.setPageMargins(QtCore.QMarginsF(0.0, 0.0, 0.0, 0.0), QtGui.QPageLayout.Unit.Millimeter)

        p = QPainter(printer)
        source = QtCore.QRectF(0, 0, self.width(), self.height())
        target = QRectF(0, 0, source.size().width() * scale, source.size().height() * scale)

        self.render(p, target, source)
        p.end()

        # 3. Réafficher les lignes guides une fois l'aperçu généré
        for g in guides:
            g.show()

    def printPage(self):
        print("Print page")

    def drawGid(self):
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
        group.setFlags(
            QGraphicsItemGroup.GraphicsItemFlag.ItemIsMovable | QGraphicsItemGroup.GraphicsItemFlag.ItemIsSelectable)

    def newStamp(self, lastStampObj):
        """Create and place a new stamp item from StampDlg."""
        dlg = StampDlg(lastStampObj, self)
        res = dlg.exec()

        if res == 1:
            stampNbr = dlg.currentStampNbr
            lastStampObj['year'] = dlg.eYear.text()
            lastStampObj['type'] = dlg.stampTypeCombo.currentText()
            lastStampObj['country'] = dlg.currentCountry
            lastStampObj['nbr'] = stampNbr
            return lastStampObj

    def newLabel(self):
        """Prompt user for text and place a standard label."""
        textLabel = QGraphicsTextItem("")
        textLabelFont = textLabel.font()
        textLabelFont.setPointSize(10)
        textLabel.setFont(textLabelFont)

        dlg = TextDlg(textLabel)
        res = dlg.exec()

        if res == 1:
            text = dlg.eTXT.toPlainText()
            font = dlg.eTXT.font()
            align = dlg.eTXT.alignment()
            self.addTextLabel(text, 50, 50, font, align)

    def newCopyRight(self):
        """Add a copyright footer to the page."""
        text = "CopyRight © Boris du Reau 2003-2026"
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
            self.addTextLabel(pageName, (self.page_width_mm / (25.4 / 96)) - 60 - textWidth, 1045, font, align,
                              "labelPageNbr")
        else:
            self.addTextLabel(pageName, (self.page_height_mm / (25.4 / 96)) - 60 - textWidth, 710, font, align,
                              "labelPageNbr")

    def addPageYear(self):
        """Prompt user for year and place a header year label."""
        textLabel = QGraphicsTextItem("")
        textLabelFont = textLabel.font()
        textLabelFont.setPointSize(10)
        textLabelFont.setBold(True)
        textLabel.setFont(textLabelFont)

        dlg = TextDlg(textLabel)
        res = dlg.exec()

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
        px_w = self.page_width_mm / (25.4 / 96)
        px_h = self.page_height_mm / (25.4 / 96)
        if self.pageType == "portrait":
            self.addTextLabel(year, (px_w - textWidth) / 2, 80, font, align, "labelYear")
        else:
            self.addTextLabel(year, (px_h - textWidth) / 2, 80, font, Qt.AlignmentFlag.AlignLeft, "labelYear")

    def alignTop(self):
        topY = 0.0
        if self.countSelectedItems() > 1:
            for it in self.items():
                if topY == 0.0 and it.isSelected() and it.parentItem() is None:
                    topY = it.y()
                if it.y() < topY and it.isSelected() and it.parentItem() is None:
                    topY = it.y()

            for it2 in self.items():
                if it2.isSelected() and it2.parentItem() is None:
                    it2.setPos(it2.x(), topY)

    def alignBottom(self):
        topY = 0.0
        if self.countSelectedItems() > 1:
            for it in self.items():
                if (it.y() + it.boundingRect().size().height()) > topY and it.isSelected() and it.parentItem() is None:
                    topY = it.y() + it.boundingRect().size().height()

            for it2 in self.items():
                if it2.isSelected() and it2.parentItem() is None:
                    it2.setPos(it2.x(), topY - it2.boundingRect().height())

    def alignLeft(self):
        topX = self.sceneRect().width()
        if self.countSelectedItems() > 1:
            for it in self.items():
                if topX == 0:
                    topX = it.x()
                if it.x() < topX and it.isSelected() and it.parentItem() is None:
                    topX = it.x()
            for it2 in self.items():
                if it2.isSelected() and it2.parentItem() is None:
                    it2.setPos(topX, it2.y())

    def alignRight(self):
        topX = 0.0
        if self.countSelectedItems() > 1:
            for it in self.items():
                if (it.x() + it.boundingRect().size().width()) > topX and it.isSelected() and it.parentItem() is None:
                    topX = (it.x() + it.boundingRect().size().width())
            for it2 in self.items():
                if it2.isSelected() and it2.parentItem() is None:
                    it2.setPos(topX - it2.boundingRect().size().width(), it2.y())

    def distributeHorizontally_old(self):
        itemLength = 0
        minX = 0
        maxX = 0
        nbrItems = 0
        posX = []

        if self.countSelectedItems() > 2:
            for it in self.items():
                if it.isSelected() and it.parentItem() is None:
                    nbrItems += 1
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
                    itemLength += it.boundingRect().size().width()

            space = (maxX - minX - itemLength) / (nbrItems - 1)
            posX.sort()

            nextX = minX
            for px in posX:
                for i in self.items():
                    if i.isSelected() and i.parentItem() is None and px == i.x():
                        i.setPos(nextX, i.y())
                        if i.type().real == 8:
                            nextX += i.boundingRect().size().width() + space
                        elif i.type().real == 10 and i.data(0) == "stampGroup":
                            stampItems = i.childItems()
                            for stampItem in stampItems:
                                if stampItem.type().real == 3:
                                    nextX += i.boundingRect().size().width() + space

    def distributeHorizontally(self):
        # Sécurité : nécessite au moins 3 objets pour distribuer horizontalement
        if self.countSelectedItems() < 3:
            return

        itemLength = 0
        minX = 0
        maxX = 0
        nbrItems = 0
        posX = []

        for it in self.items():
            if it.isSelected() and it.parentItem() is None:
                nbrItems += 1
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
                itemLength += it.boundingRect().size().width()

        if nbrItems > 2 and (nbrItems - 1) > 0:
            space = (maxX - minX - itemLength) / (nbrItems - 1)
            posX.sort()

            nextX = minX
            for px in posX:
                for i in self.items():
                    if i.isSelected() and i.parentItem() is None and px == i.x():
                        i.setPos(nextX, i.y())
                        if i.type().real == 8:
                            nextX += i.boundingRect().size().width() + space
                        elif i.type().real == 10 and i.data(0) == "stampGroup":
                            stampItems = i.childItems()
                            for stampItem in stampItems:
                                if stampItem.type().real == 3:
                                    nextX += i.boundingRect().size().width() + space

    def distributeVertically_old(self):
        itemLength = 0
        minY = 0
        maxY = 0
        nbrItems = 0
        posY = []
        if self.countSelectedItems() > 2:
            print(self.countSelectedItems())
            for it in self.items():
                if it.isSelected() and it.parentItem() is None:
                    nbrItems += 1
                    if minY == 0:
                        minY = it.y()
                    if it.y() < minY:
                        minY = it.y()
                    if (it.y() + it.boundingRect().size().height()) > maxY:
                        maxY = it.y() + it.boundingRect().size().height()

                    posY.append(it.y())
                    itemLength += it.boundingRect().size().height()

            space = (maxY - minY - itemLength) / (nbrItems - 1)
            posY.sort()
            nextY = minY
            for py in posY:
                for i in self.items():
                    if i.isSelected() and i.parentItem() is None and py == i.y():
                        i.setPos(i.x(), nextY)
                        nextY += i.boundingRect().size().height() + space

    def distributeVertically(self):
        # Sécurité : nécessite au moins 3 objets pour distribuer verticalement
        if self.countSelectedItems() < 3:
            return

        itemLength = 0
        minY = 0
        maxY = 0
        nbrItems = 0
        posY = []

        for it in self.items():
            if it.isSelected() and it.parentItem() is None:
                nbrItems += 1
                if minY == 0:
                    minY = it.y()
                if it.y() < minY:
                    minY = it.y()
                if (it.y() + it.boundingRect().size().height()) > maxY:
                    maxY = it.y() + it.boundingRect().size().height()

                posY.append(it.y())
                itemLength += it.boundingRect().size().height()

        if nbrItems > 2 and (nbrItems - 1) > 0:
            space = (maxY - minY - itemLength) / (nbrItems - 1)
            posY.sort()
            nextY = minY
            for py in posY:
                for i in self.items():
                    if i.isSelected() and i.parentItem() is None and py == i.y():
                        i.setPos(i.x(), nextY)
                        nextY += i.boundingRect().size().height() + space

    def centerHorizontally(self):
        if self.countSelectedItems() > 0:
            for it in self.items():
                if it.isSelected() and it.parentItem() is None:
                    centerPage = self.sceneRect().width() / 2
                    if it.type().real == 8:
                        centerItem = it.boundingRect().width() / 2
                        it.setPos((centerPage - centerItem), it.y())
                    elif it.type().real == 10 and it.data(0) == "stampGroup":
                        stampItems = it.childItems()
                        for stampItem in stampItems:
                            if stampItem.type().real == 3:
                                if stampItem.x() < 0:
                                    centerItem = (it.boundingRect().width() / 2) + stampItem.x()
                                    it.setPos((centerPage - centerItem), it.y())
                                else:
                                    centerItem = it.boundingRect().width() / 2
                                    it.setPos((centerPage - centerItem), it.y())

    def centerVertically(self):
        if self.countSelectedItems() > 0:
            for it in self.items():
                if it.isSelected() and it.parentItem() is None:
                    centerPage = self.sceneRect().height() / 2
                    centerItem = it.boundingRect().height() / 2
                    it.setPos(it.x(), centerPage - centerItem)

    def countSelectedItems(self):
        selected = 0
        for it in self.items():
            if it.isSelected():
                selected += 1
        return selected

    def addImage(self, fileName):
        if fileName:
            pixmap = QPixmap(fileName)
            if not pixmap.isNull():
                pixmapitem = ResizablePixmapItem(pixmap)
                pixmapitem.setPos(50, 50)
                self.addItem(pixmapitem)

    def mouseDoubleClickEvent(self, event):
        """Fallback double-click handling if not caught by GraphicsView."""
        item = self.itemAt(event.scenePos(), QtGui.QTransform())
        if item:
            top_item = item
            while top_item.parentItem() is not None:
                top_item = top_item.parentItem()

            event.accept()
            self.editObject(top_item)
        else:
            super().mouseDoubleClickEvent(event)

    def mousePressEvent_old(self, event):
        """Record initial positions for items before drag operations and preserve text item selection."""
        scene_pos = event.scenePos()
        items_under_cursor = self.items(scene_pos)

        # Filtrer pour éviter de sélectionner la bordure si on clique sur un texte
        for item in items_under_cursor:
            top_item = item
            while top_item.parentItem() is not None:
                top_item = top_item.parentItem()
            data_type = str(top_item.data(0)) if top_item.data(0) is not None else ""
            if data_type != "borderGroup":
                top_item.setSelected(True)
                break

        self.mouse_press_positions = {
            item: item.pos() for item in self.selectedItems() if item.parentItem() is None
        }
        super().mousePressEvent(event)

    def mousePressEvent(self, event):
        """Gère la sélection unitaire ou multiple par Ctrl+Clic et le déplacement."""
        scene_pos = event.scenePos()
        self._press_scene_pos = scene_pos
        items_under_cursor = self.items(scene_pos)

        # 1. Identifier le premier objet sous le curseur (en ignorant la bordure)
        target_item = None
        for item in items_under_cursor:
            top_item = item
            while top_item.parentItem() is not None:
                top_item = top_item.parentItem()
            data_type = str(top_item.data(0)) if top_item.data(0) is not None else ""
            if data_type != "borderGroup":
                target_item = top_item
                break

        is_ctrl = bool(event.modifiers() & Qt.KeyboardModifier.ControlModifier)
        self._single_click_item = None

        if event.button() == Qt.MouseButton.LeftButton:
            if is_ctrl:
                # Mode Ctrl maintenu : bascule l'état (sélectionne ou désélectionne)
                if target_item is not None:
                    target_item.setSelected(not target_item.isSelected())

                self.mouse_press_positions = {
                    it: it.pos() for it in self.selectedItems() if it.parentItem() is None
                }
                event.accept()
                return  # On sort pour empêcher Qt d'interférer avec les sous-éléments

            else:
                # Clic simple sans Ctrl
                if target_item is not None:
                    if not target_item.isSelected():
                        # Si l'objet n'était pas sélectionné, il devient le seul sélectionné
                        self.clearSelection()
                        target_item.setSelected(True)
                    else:
                        # S'il était déjà sélectionné parmi d'autres, on garde la sélection
                        # en prévision d'un déplacement groupé, mais on note l'item
                        if len(self.selectedItems()) > 1:
                            self._single_click_item = target_item
                else:
                    # Clic dans le vide ou sur la bordure : tout désélectionner
                    self.clearSelection()

        # Enregistrement des positions initiales pour l'Undo (MoveCommand)
        self.mouse_press_positions = {
            item: item.pos() for item in self.selectedItems() if item.parentItem() is None
        }
        super().mousePressEvent(event)

    def mouseReleaseEvent_old(self, event):
        super().mouseReleaseEvent(event)

        moved_items = []
        old_positions = []

        for item, old_pos in self.mouse_press_positions.items():
            if hasattr(item, 'is_resizing') and item.is_resizing:
                continue

            if item.pos() != old_pos:
                moved_items.append(item)
                old_positions.append(old_pos)

        if moved_items:
            cmd = MoveCommand(moved_items, old_positions)
            self.undoStack.push(cmd)

        self.mouse_press_positions.clear()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

        # Si on a cliqué sans Ctrl sur un objet déjà dans un groupe sans le déplacer,
        # on réduit la sélection à ce seul objet
        if hasattr(self, '_single_click_item') and self._single_click_item is not None:
            if hasattr(self, '_press_scene_pos'):
                drag_distance = (event.scenePos() - self._press_scene_pos).manhattanLength()
                if drag_distance < 4:
                    self.clearSelection()
                    self._single_click_item.setSelected(True)
            self._single_click_item = None

        # Gestion de l'historique d'annulation (Undo)
        moved_items = []
        old_positions = []

        for item, old_pos in self.mouse_press_positions.items():
            if hasattr(item, 'is_resizing') and item.is_resizing:
                continue

            if item.pos() != old_pos:
                moved_items.append(item)
                old_positions.append(old_pos)

        if moved_items:
            cmd = MoveCommand(moved_items, old_positions)
            self.undoStack.push(cmd)

        self.mouse_press_positions.clear()

    def autoArrangeStamps(self):
        """Organise et aligne harmonieusement les timbres sélectionnés ou tous les timbres."""
        # 1. Sélectionner les timbres à organiser
        selected_stamps = [
            it for it in self.selectedItems()
            if it.parentItem() is None and it.data(0) == "stampGroup"
        ]
        # Si moins de 2 timbres sont sélectionnés, on organise tous les timbres de la page
        stamps = selected_stamps if len(selected_stamps) > 1 else [
            it for it in self.items()
            if it.parentItem() is None and it.data(0) == "stampGroup"
        ]

        if not stamps:
            return

        # Sauvegarder les positions pour le "Undo"
        old_positions = [it.pos() for it in stamps]

        # 2. Regrouper les timbres en rangées (clustering basé sur la position Y)
        stamps_by_y = sorted(stamps, key=lambda s: s.y())
        rows = []
        y_threshold = 100.0  # Tolérance pour considérer que des timbres sont sur la même ligne

        for stamp in stamps_by_y:
            placed = False
            for row in rows:
                # Si le timbre est proche de la ligne actuelle en Y
                avg_y = sum(s.y() for s in row) / len(row)
                if abs(stamp.y() - avg_y) < y_threshold:
                    row.append(stamp)
                    placed = True
                    break
            if not placed:
                rows.append([stamp])

        # Trier les timbres de gauche à droite dans chaque rangée
        for row in rows:
            row.sort(key=lambda s: s.x())

        # Trier les rangées de haut en bas
        rows.sort(key=lambda r: sum(s.y() for s in r) / len(r))

        # 3. Paramètres de mise en page
        page_w = self.sceneRect().width()
        page_h = self.sceneRect().height()

        # Marges estimées d'après les images (laissant de la place pour le titre/année et le copyright)
        margin_top = 200.0
        margin_bottom = page_h - 150.0
        available_h = max(200.0, margin_bottom - margin_top)

        # Calculer la hauteur de chaque rangée
        row_heights = [max(s.boundingRect().height() for s in row) for row in rows]
        total_rows_h = sum(row_heights)

        # Calculer l'espacement vertical (v_gap) entre les rangées
        if len(rows) > 1:
            v_gap = (available_h - total_rows_h) / (len(rows) - 1)
            # Limiter l'espacement vertical pour que ce ne soit ni trop collé ni trop étiré
            v_gap = max(20.0, min(v_gap, 100.0))
        else:
            v_gap = 50.0

        # Recalculer le point de départ Y pour centrer verticalement le bloc entier
        total_block_h = total_rows_h + (len(rows) - 1) * v_gap
        current_y = margin_top + max(0.0, (available_h - total_block_h) / 2.0)

        # Espacement horizontal fixe entre les timbres (peut être ajusté)
        h_spacing = 40.0

        # 4. Appliquer les nouvelles positions
        for i, row in enumerate(rows):
            # Calculer la largeur totale de la rangée pour la centrer horizontalement
            row_width = sum(s.boundingRect().width() for s in row) + (len(row) - 1) * h_spacing
            start_x = (page_w - row_width) / 2.0

            # Aligner les cadres (stampBox) plutôt que le haut du groupe (qui inclut le titre s'il y en a)
            box_offsets = []
            for stamp in row:
                box = next((c for c in stamp.childItems() if c.data(0) == "stampBox"), None)
                box_offsets.append(box.y() if box else 0.0)

            target_box_offset = max(box_offsets) if box_offsets else 0.0

            current_x = start_x
            for j, stamp in enumerate(row):
                # Ajuster le Y pour que les stampBox soient alignées sur la ligne
                y_adjust = target_box_offset - box_offsets[j]

                new_x = current_x - stamp.boundingRect().x()
                new_y = current_y + y_adjust - stamp.boundingRect().y()

                stamp.setPos(new_x, new_y)
                current_x += stamp.boundingRect().width() + h_spacing

            current_y += row_heights[i] + v_gap

        # 5. Enregistrer le déplacement pour la fonction "Undo" (Annuler)
        moved_items = []
        old_moved_positions = []
        for it, old_pos in zip(stamps, old_positions):
            if it.pos() != old_pos:
                moved_items.append(it)
                old_moved_positions.append(old_pos)

        if moved_items:
            cmd = MoveCommand(moved_items, old_moved_positions)
            self.undoStack.push(cmd)

    def clearGuides(self):
        """Supprime toutes les lignes guides de la page."""
        guides = [it for it in self.items() if it.data(0) == "guideLine"]
        for g in guides:
            self.removeItem(g)

    def replaceBorder(self, new_style):
        """Remplace la bordure existante par un nouveau style, ou en crée une si elle n'existe pas."""
        old_border = None

        # Chercher la bordure actuelle sur la page
        for item in self.items():
            if item.data(0) == "borderGroup":
                old_border = item
                break

        if old_border:
            # Récupérer les dimensions et la position de l'ancienne bordure
            w = old_border.data(1)
            h = old_border.data(2)
            pos = old_border.pos()

            # Supprimer l'ancienne bordure
            self.removeItem(old_border)

            # Générer la nouvelle et la placer exactement au même endroit
            new_border = PageBorder(w, h, style=new_style)
            new_border.setPos(pos)
            self.addItemWithUndo(new_border, _("Changer la bordure"))
        else:
            # Si aucune bordure n'était présente, on en génère une standard
            paper_format = self.get_configured_paper_format()
            if paper_format == "Letter":
                w_mm, h_mm = 215.9, 279.4
            else:
                w_mm, h_mm = 210.0, 297.0

            if self.pageType == "portrait":
                border_w = (w_mm - 33.0) / (25.4 / 96.0)
                border_h = (h_mm - 25.0) / (25.4 / 96.0)
                margin_l = 19.0 / (25.4 / 96.0)
                self.addBorder(border_w, border_h, margin_l, 0, 0, 0, new_style)
            else:
                border_w = (h_mm - 25.0) / (25.4 / 96.0)
                border_h = (w_mm - 33.0) / (25.4 / 96.0)
                margin_l = (((h_mm / (25.4 / 96.0)) - border_w) / 2)
                margin_t = 19.0 / (25.4 / 96.0)
                self.addBorder(border_w, border_h, margin_l, 0, margin_t, 0, new_style)