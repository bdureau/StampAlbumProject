"""
Resizable Pixmap Item Module
----------------------------
Custom QGraphicsPixmapItem with smooth, interactive corner handles for resizing.
Includes full-bounding-box hit-testing to support transparent PNGs seamlessly.

Author: Boris du Reau
"""

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtWidgets import QGraphicsPixmapItem, QGraphicsItem
from PyQt6.QtGui import QPen, QBrush, QColor, QPainter, QPainterPath


class ResizablePixmapItem(QGraphicsPixmapItem):
    """Graphics pixmap item with interactive corner handles for resizing."""

    HANDLE_SIZE = 10.0  # Size of handles in screen pixels

    def __init__(self, pixmap, parent=None):
        super().__init__(pixmap, parent)

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        self.is_resizing = False
        self.active_handle = None
        self.start_scene_pos = None
        self.start_scale = 1.0

    def shape(self):
        """
        CRITICAL FIX FOR TRANSPARENT IMAGES:
        Override shape() to use a full solid rectangle for hit-testing.
        Otherwise, Qt ignores mouse clicks on transparent/alpha pixels.
        """
        path = QPainterPath()
        path.addRect(self.boundingRect())
        return path

    def boundingRect(self):
        """Returns exact bounding rect plus margin for resize handles."""
        pixmap = self.pixmap()
        if pixmap.isNull():
            return QRectF()

        rect = QRectF(0, 0, pixmap.width(), pixmap.height())
        current_scale = max(self.scale(), 0.001)
        margin = (self.HANDLE_SIZE / current_scale) / 2.0
        return rect.adjusted(-margin, -margin, margin, margin)

    def get_handles(self):
        """Returns the 4 corner handle rectangles in local coordinates."""
        pixmap = self.pixmap()
        w = pixmap.width()
        h = pixmap.height()

        current_scale = max(self.scale(), 0.001)
        s = self.HANDLE_SIZE / current_scale
        hs = s / 2.0

        return {
            'top_left': QRectF(-hs, -hs, s, s),
            'top_right': QRectF(w - hs, -hs, s, s),
            'bottom_left': QRectF(-hs, h - hs, s, s),
            'bottom_right': QRectF(w - hs, h - hs, s, s),
        }

    def paint(self, painter: QPainter, option, widget=None):
        """Draw image with smooth scaling and render selection outline/handles."""
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        super().paint(painter, option, widget)

        if self.isSelected():
            pixmap = self.pixmap()
            if pixmap.isNull():
                return
            w, h = pixmap.width(), pixmap.height()

            current_scale = max(self.scale(), 0.001)

            # Draw selection bounding box (no fill)
            painter.setPen(QPen(QColor("#0078d7"), 1.0 / current_scale, Qt.PenStyle.SolidLine))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(QRectF(0, 0, w, h))

            # Draw corner handles (solid white fill)
            painter.setPen(QPen(QColor("#0078d7"), 1.0 / current_scale, Qt.PenStyle.SolidLine))
            painter.setBrush(QBrush(QColor("#ffffff")))
            for handle_rect in self.get_handles().values():
                painter.drawRect(handle_rect)

    def mousePressEvent(self, event):
        """Check for clicks on handles even over transparent pixels."""
        if self.isSelected() and event.button() == Qt.MouseButton.LeftButton:
            pos = event.pos()
            for handle_name, handle_rect in self.get_handles().items():
                if handle_rect.contains(pos):
                    self.is_resizing = True
                    self.active_handle = handle_name
                    self.start_scene_pos = event.scenePos()
                    self.start_scale = self.scale()
                    event.accept()
                    return

        self.is_resizing = False
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Proportionally scale image while dragging handle."""
        if self.is_resizing:
            delta = event.scenePos() - self.start_scene_pos
            orig_w = self.pixmap().width()

            if orig_w == 0:
                return

            if self.active_handle in ['top_right', 'bottom_right']:
                delta_width = delta.x()
            else:
                delta_width = -delta.x()

            current_width = orig_w * self.start_scale
            new_width = max(20.0, current_width + delta_width)
            new_scale = new_width / orig_w

            self.prepareGeometryChange()
            self.setScale(new_scale)
            self.update()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Release resize lock and record Undo command if scale changed."""
        if self.is_resizing:
            self.is_resizing = False
            self.active_handle = None

            if self.scale() != self.start_scale and self.scene() and hasattr(self.scene(), 'undoStack'):
                from UndoCommands import ResizeItemCommand
                cmd = ResizeItemCommand(self, self.start_scale, self.scale())
                self.scene().undoStack.push(cmd)

            event.accept()
        else:
            super().mouseReleaseEvent(event)