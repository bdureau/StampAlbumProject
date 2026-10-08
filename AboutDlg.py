"""
About Dialog Module
-------------------
Displays information about the Stamp Album application, its features,
and author details in both French and English with scrollable text.

Author: Boris du Reau
"""

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QTextBrowser, QDialogButtonBox
)
from PyQt6.QtGui import QPixmap, QFont


class AboutDlg(QDialog):
    """Scrollable 'About' dialog displaying application overview in FR/EN."""

    def __init__(self, parent=None):
        super(AboutDlg, self).__init__(parent)
        self.setWindowTitle("À propos de Stamp Album / About Stamp Album")
        self.resize(550, 450)
        self.createDlg()

    def createDlg(self):
        main_layout = QVBoxLayout()

        # Header layout (Icon + Title)
        header_layout = QHBoxLayout()

        logo = QLabel()
        pixmap = QPixmap('stamp_book1170.png')
        if not pixmap.isNull():
            logo.setPixmap(pixmap.scaledToWidth(64, Qt.TransformationMode.SmoothTransformation))
        header_layout.addWidget(logo)

        title_label = QLabel("Stamp Album")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        main_layout.addLayout(header_layout)

        # Scrollable text browser with HTML content
        text_browser = QTextBrowser()
        text_browser.setOpenExternalLinks(True)
        text_browser.setHtml(self.get_about_text_html())
        main_layout.addWidget(text_browser)

        # OK Button
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        main_layout.addWidget(button_box)

        self.setLayout(main_layout)

    def get_about_text_html(self) -> str:
        """Return the bilingual description formatted in HTML."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: sans-serif; font-size: 11pt; line-height: 1.4; color: #222; }
                h2 { color: #1a365d; border-bottom: 1px solid #cbd5e0; padding-bottom: 4px; margin-top: 15px; }
                h3 { color: #2b6cb0; margin-bottom: 5px; }
                ul { margin-left: -15px; }
                li { margin-bottom: 4px; }
                .author { font-style: italic; color: #4a5568; margin-bottom: 15px; }
                .hr-divider { border: 0; height: 1px; background: #e2e8f0; margin: 20px 0; }
            </style>
        </head>
        <body>
            <!-- VERSION FRANÇAISE -->
            <h2>À propos de Stamp Album</h2>
            <div class="author">
                <b>Auteur :</b> Boris du Reau<br>
                <b>Version :</b> 5.0.3 (2003-2026)
            </div>

            <h3>Description de l'application</h3>
            <p>
                <b>Stamp Album</b> est une application de création et de mise en page de pages 
                d'albums de timbres personnalisées. Initialement développée en VBA au début des 
                années 2000, elle a été entièrement réécrite en Python 3 et PyQt6.
            </p>

            <h3>Fonctionnalités principales</h3>
            <ul>
                <li><b>Gestion de catalogues :</b> Connexion à des bases de données de timbres (SQLite / Access) classées par pays, types et années.</li>
                <li><b>Mise en page graphique :</b> Positionnement précis des timbres, pochettes, titres, valeurs nominales et illustrations.</li>
                <li><b>Outils d'alignement :</b> Alignement automatique (gauche, droite, haut, bas) et distribution uniforme horizontale ou verticale.</li>
                <li><b>Personnalisation :</b> Ajout de bordures de pages de haute précision, numéros de pages,copyrights et années.</li>
                <li><b>Impression et Export :</b> Aperçu avant impression haute résolution et exportation d'albums complets ou de pages individuelles au format PDF.</li>
            </ul>

            <hr class="hr-divider">

            <!-- ENGLISH VERSION -->
            <h2>About Stamp Album</h2>
            <div class="author">
                <b>Author:</b> Boris du Reau<br>
                <b>Version:</b> 5.0.3 (2003-2026)
            </div>

            <h3>Application Overview</h3>
            <p>
                <b>Stamp Album</b> is a desktop application designed to create and assemble custom 
                stamp album pages. Originally written in VBA in the early 2000s, it has been 
                fully modernized and re-engineered using Python 3 and PyQt6.
            </p>

            <h3>Key Features</h3>
            <ul>
                <li><b>Catalogue Management:</b> Connects to country-specific stamp databases (SQLite / Access) organized by category, year, and catalogue numbers.</li>
                <li><b>Graphic Layout:</b> Precise placement of stamp mounts, illustrations, titles, nominal values, and descriptors.</li>
                <li><b>Alignment Tools:</b> Automatic item alignment (left, right, top, bottom) and equal horizontal/vertical distribution.</li>
                <li><b>Page Customization:</b> Insert decorative page borders, page numbers, copyright notices, and header years.</li>
                <li><b>Printing & Export:</b> High-resolution print preview and single/multi-page PDF export capabilities.</li>
            </ul>
        </body>
        </html>
        """