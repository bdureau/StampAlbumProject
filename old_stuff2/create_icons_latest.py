import os
import sys
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QPixmap, QColor, QPen, QBrush, QPainterPath
from PyQt6.QtWidgets import QApplication

def create_icons():
    app = QApplication.instance() or QApplication(sys.argv)
    os.makedirs("../images", exist_ok=True)
    size = 32

    # ---------------------------------------------------------
    # 1. Icône : Changer la bordure de TOUTES les pages
    # ---------------------------------------------------------
    pixmap_border_all = QPixmap(size, size)
    pixmap_border_all.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap_border_all)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    page_brush = QBrush(QColor("#ffffff"))
    border_pen = QPen(QColor("#c0392b"), 2) # Bordure rouge brique pour bien la voir
    outline_pen = QPen(QColor("#2c3e50"), 1)

    # Page en arrière-plan
    painter.setPen(outline_pen)
    painter.setBrush(page_brush)
    painter.drawRect(12, 10, 16, 20)
    painter.setPen(border_pen)
    painter.drawRect(15, 13, 10, 14)

    # Page au premier plan
    painter.setPen(outline_pen)
    painter.setBrush(page_brush)
    painter.drawRect(4, 4, 16, 20)
    painter.setPen(border_pen)
    painter.drawRect(7, 7, 10, 14)

    painter.end()
    pixmap_border_all.save("images/border_all.png", "PNG")

    # ---------------------------------------------------------
    # 2. Icône : Planche Contact (Miniatures)
    # ---------------------------------------------------------
    pixmap_thumbs = QPixmap(size, size)
    pixmap_thumbs.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap_thumbs)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    page_brush = QBrush(QColor("#ffffff"))
    page_pen = QPen(QColor("#2980b9"), 1.5) # Bordure bleue
    painter.setPen(page_pen)
    painter.setBrush(page_brush)

    # Dessin d'une grille 3x3 de mini-pages
    for x in [3, 13, 23]:
        for y in [3, 13, 23]:
            painter.drawRect(x, y, 6, 8)

    painter.end()
    pixmap_thumbs.save("images/thumbnails.png", "PNG")

    # ---------------------------------------------------------
    # 3. Icône : Rich Text (Texte Formaté)
    # ---------------------------------------------------------
    pixmap_rich = QPixmap(size, size)
    pixmap_rich.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap_rich)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Document de fond
    painter.setPen(QPen(QColor("#7f8c8d"), 1))
    painter.setBrush(QBrush(QColor("#ecf0f1")))
    painter.drawRect(4, 4, 24, 24)

    # Lignes de texte colorées pour montrer le côté "Riche"
    painter.setPen(QPen(QColor("#c0392b"), 2)) # Rouge
    painter.drawLine(8, 10, 24, 10)
    painter.setPen(QPen(QColor("#27ae60"), 2)) # Vert
    painter.drawLine(8, 16, 20, 16)
    painter.setPen(QPen(QColor("#2980b9"), 2)) # Bleu
    painter.drawLine(8, 22, 24, 22)

    # Petite étincelle "Magique/Formatage" en bas à droite
    sparkle = QPainterPath()
    cx, cy = 24.0, 24.0
    r_out = 6.0
    r_in = 2.0
    sparkle.moveTo(cx, cy - r_out)
    sparkle.quadTo(cx, cy, cx + r_out, cy)
    sparkle.quadTo(cx, cy, cx, cy + r_out)
    sparkle.quadTo(cx, cy, cx - r_out, cy)
    sparkle.quadTo(cx, cy, cx, cy - r_out)
    sparkle.closeSubpath()
    painter.setPen(QPen(QColor("#d35400"), 0.8))
    painter.setBrush(QBrush(QColor("#f39c12")))
    painter.drawPath(sparkle)

    painter.end()
    pixmap_rich.save("images/rich_text.png", "PNG")

    print("Les 3 icônes ont été générées avec succès dans le dossier 'images'.")

if __name__ == "__main__":
    create_icons()