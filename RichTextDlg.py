"""
Rich Text Dialog Module
-----------------------
Provides a rich-text editor with formatting options for font, size, color,
styles, and paragraph alignment.

Author: Boris du Reau
"""
import gettext
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QTextCharFormat, QTextBlockFormat
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit,
    QSpinBox, QToolButton, QColorDialog, QDialogButtonBox, QFontComboBox
)
# Set up gettext localization
gettext.find("RichTextDlg")
translate = gettext.translation('RichTextDlg', localedir='locale', languages=['fr'], fallback=True)
translate.install()
_ = translate.gettext

class RichTextDlg(QDialog):
    """Dialog allowing full rich-text formatting for QGraphicsTextItem."""

    def __init__(self, text_item=None, parent=None):
        super().__init__(parent)
        #self.setWindowTitle("Rich Text Editor")
        self.setWindowTitle(_("Rich Text Editor"))
        self.resize(600, 400)
        self.text_item = text_item

        self._create_ui()
        if self.text_item:
            self.editor.blockSignals(True)
            self.editor.setHtml(self.text_item.toHtml())
            self.editor.blockSignals(False)

    def _create_ui(self):
        layout = QVBoxLayout(self)

        # --- Formatting Toolbar ---
        toolbar = QHBoxLayout()

        # Font family picker
        self.font_combo = QFontComboBox()
        self.font_combo.setToolTip(_("Font Family"))
        self.font_combo.currentFontChanged.connect(self._set_font_family)
        toolbar.addWidget(self.font_combo)

        # Font size picker
        self.size_spin = QSpinBox()
        self.size_spin.setRange(6, 144)
        self.size_spin.setValue(12)
        self.size_spin.setToolTip(_("Font Size"))
        self.size_spin.valueChanged.connect(self._set_font_size)
        toolbar.addWidget(self.size_spin)

        # Bold, Italic, Underline buttons
        self.btn_bold = QToolButton()
        self.btn_bold.setText(_("B"))
        self.btn_bold.setToolTip(_("Bold"))
        self.btn_bold.setCheckable(True)
        self.btn_bold.setStyleSheet("font-weight: bold;")
        self.btn_bold.clicked.connect(self._toggle_bold)
        toolbar.addWidget(self.btn_bold)

        self.btn_italic = QToolButton()
        self.btn_italic.setText(_("I"))
        self.btn_italic.setToolTip(_("Italic"))
        self.btn_italic.setCheckable(True)
        self.btn_italic.setStyleSheet("font-style: italic;")
        self.btn_italic.clicked.connect(self._toggle_italic)
        toolbar.addWidget(self.btn_italic)

        self.btn_underline = QToolButton()
        self.btn_underline.setText(_("U"))
        self.btn_underline.setToolTip(_("Underline"))
        self.btn_underline.setCheckable(True)
        self.btn_underline.setStyleSheet("text-decoration: underline;")
        self.btn_underline.clicked.connect(self._toggle_underline)
        toolbar.addWidget(self.btn_underline)

        # Text color picker
        self.btn_color = QToolButton()
        self.btn_color.setText("🎨")
        self.btn_color.setToolTip(_("Text Color"))
        self.btn_color.clicked.connect(self._choose_color)
        toolbar.addWidget(self.btn_color)

        # Paragraph alignment buttons
        self.btn_align_left = QToolButton()
        self.btn_align_left.setText(_("Left"))
        self.btn_align_left.setToolTip(_("Align Left"))
        self.btn_align_left.clicked.connect(lambda: self._set_alignment(Qt.AlignmentFlag.AlignLeft))
        toolbar.addWidget(self.btn_align_left)

        self.btn_align_center = QToolButton()
        self.btn_align_center.setText(_("Center"))
        self.btn_align_center.setToolTip(_("Center"))
        self.btn_align_center.clicked.connect(lambda: self._set_alignment(Qt.AlignmentFlag.AlignCenter))
        toolbar.addWidget(self.btn_align_center)

        self.btn_align_right = QToolButton()
        self.btn_align_right.setText(_("Right"))
        self.btn_align_right.setToolTip(_("Align Right"))
        self.btn_align_right.clicked.connect(lambda: self._set_alignment(Qt.AlignmentFlag.AlignRight))
        toolbar.addWidget(self.btn_align_right)

        self.btn_align_justify = QToolButton()
        self.btn_align_justify.setText(_("Justify"))
        self.btn_align_justify.setToolTip(_("Justify"))
        self.btn_align_justify.clicked.connect(lambda: self._set_alignment(Qt.AlignmentFlag.AlignJustify))
        toolbar.addWidget(self.btn_align_justify)

        layout.addLayout(toolbar)

        # --- Text Editor Area ---
        self.editor = QTextEdit()
        self.editor.cursorPositionChanged.connect(self._update_format_controls)
        layout.addWidget(self.editor)

        # --- Standard OK / Cancel Buttons ---
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _set_font_family(self, font):
        fmt = QTextCharFormat()
        fmt.setFontFamily(font.family())
        self._apply_char_format(fmt)

    def _set_font_size(self, size):
        fmt = QTextCharFormat()
        fmt.setFontPointSize(float(size))
        self._apply_char_format(fmt)

    def _toggle_bold(self):
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Weight.Bold if self.btn_bold.isChecked() else QFont.Weight.Normal)
        self._apply_char_format(fmt)

    def _toggle_italic(self):
        fmt = QTextCharFormat()
        fmt.setFontItalic(self.btn_italic.isChecked())
        self._apply_char_format(fmt)

    def _toggle_underline(self):
        fmt = QTextCharFormat()
        fmt.setFontUnderline(self.btn_underline.isChecked())
        self._apply_char_format(fmt)

    def _choose_color(self):
        color = QColorDialog.getColor(self.editor.textColor(), self, _("Select Text Color"))
        if color.isValid():
            fmt = QTextCharFormat()
            fmt.setForeground(color)
            self._apply_char_format(fmt)

    def _set_alignment(self, align_flag):
        block_fmt = QTextBlockFormat()
        block_fmt.setAlignment(align_flag)
        self.editor.textCursor().mergeBlockFormat(block_fmt)

    def _apply_char_format(self, fmt):
        cursor = self.editor.textCursor()
        if not cursor.hasSelection():
            cursor.select(cursor.SelectionType.WordUnderCursor)
        cursor.mergeCharFormat(fmt)
        self.editor.mergeCurrentCharFormat(fmt)

    def _update_format_controls(self):
        """Update toolbar button states based on current cursor position."""
        fmt = self.editor.currentCharFormat()
        if fmt.fontFamily():
            self.font_combo.blockSignals(True)
            self.font_combo.setCurrentFont(QFont(fmt.fontFamily()))
            self.font_combo.blockSignals(False)

        if fmt.fontPointSize() > 0:
            self.size_spin.blockSignals(True)
            self.size_spin.setValue(int(fmt.fontPointSize()))
            self.size_spin.blockSignals(False)

        self.btn_bold.setChecked(fmt.fontWeight() == QFont.Weight.Bold)
        self.btn_italic.setChecked(fmt.fontItalic())
        self.btn_underline.setChecked(fmt.fontUnderline())

    def get_html(self) -> str:
        return self.editor.toHtml()