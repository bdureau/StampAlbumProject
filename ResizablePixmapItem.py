"""
Resizable Pixmap Item Module
----------------------------
Custom QGraphicsPixmapItem with smooth, interactive corner handles for resizing.

Author: Boris du Reau
"""

from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtWidgets import QGraphicsPixmapItem, QGraphicsItem
from PyQt6.QtGui import QPen, QBrush, QColor, QPainter


class ResizablePixmapItem(QGraphicsPixmapItem):
    """Graphics pixmap item with interactive corner handles for resizing."""

    HANDLE_SIZE = 10.0  # Taille fixe de la poignée (en pixels)

    def __init__(self, pixmap, parent=None):
        super().__init__(pixmap, parent)

        # Activer le déplacement, la sélection et la gestion de géométrie
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        self.is_resizing = False
        self.active_handle = None
        self.start_scene_pos = None
        self.start_scale = 1.0

    def boundingRect(self):
        """Zone englobante exacte (pixmap + marge des poignées)."""
        pixmap = self.pixmap()
        if pixmap.isNull():
            return QRectF()

        rect = QRectF(0, 0, pixmap.width(), pixmap.height())
        # Marge en repère local tenant compte de l'échelle actuelle
        current_scale = max(self.scale(), 0.001)
        margin = (self.HANDLE_SIZE / current_scale) / 2.0
        return rect.adjusted(-margin, -margin, margin, margin)

    def get_handles(self):
        """Calcule les 4 poignées en gardant une taille visuelle constante à l'écran."""
        pixmap = self.pixmap()
        w = pixmap.width()
        h = pixmap.height()

        current_scale = max(self.scale(), 0.001)
        s = self.HANDLE_SIZE / current_scale  # Garde la poignée cliquable peu importe le zoom
        hs = s / 2.0

        return {
            'top_left': QRectF(-hs, -hs, s, s),
            'top_right': QRectF(w - hs, -hs, s, s),
            'bottom_left': QRectF(-hs, h - hs, s, s),
            'bottom_right': QRectF(w - hs, h - hs, s, s),
        }

    def paint(self, painter: QPainter, option, widget=None):
        """Dessine l'image, le cadre de sélection et les poignées aux coins."""
        super().paint(painter, option, widget)

        if self.isSelected():
            pixmap = self.pixmap()
            w, h = pixmap.width(), pixmap.height()

            # Dessiner le cadre bleu autour de l'image
            current_scale = max(self.scale(), 0.001)
            painter.setPen(QPen(QColor("#0078d7"), 1.0 / current_scale, Qt.PenStyle.SolidLine))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(QRectF(0, 0, w, h))

            # Dessiner les poignées blanches
            painter.setPen(QPen(QColor("#0078d7"), 1.0 / current_scale, Qt.PenStyle.SolidLine))
            painter.setBrush(QBrush(QColor("#ffffff")))
            for handle_rect in self.get_handles().values():
                painter.drawRect(handle_rect)

    def mousePressEvent(self, event):
        """Détecte l'enfoncement de la souris sur une poignée."""
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
        """Calcule et applique le redimensionnement de manière fluide."""
        if self.is_resizing:
            # Distance parcourue par la souris en coordonnées de scène
            delta = event.scenePos() - self.start_scene_pos
            orig_w = self.pixmap().width()

            if orig_w == 0:
                return

            # Axe du mouvement selon la poignée attrapée
            if self.active_handle in ['top_right', 'bottom_right']:
                delta_width = delta.x()
            else:
                delta_width = -delta.x()

            # Calcul direct de la nouvelle largeur désirée
            current_width = orig_w * self.start_scale
            new_width = max(20.0, current_width + delta_width)

            # Calcul de l'échelle correspondante
            new_scale = new_width / orig_w

            self.prepareGeometryChange()
            self.setScale(new_scale)
            self.update()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Réinitialise l'état au relâchement de la souris."""
        self.is_resizing = False
        self.active_handle = None
        super().mouseReleaseEvent(event)