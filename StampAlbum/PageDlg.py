import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QRadioButton, QGroupBox,
    QLabel, QHBoxLayout, QVBoxLayout, QDialogButtonBox, QComboBox, QFormLayout
)
from PyQt6.QtGui import QPixmap
from PageBorder import PageBorder
from SAAppPaths import get_config_value

import gettext
from AppLanguage import get_language

# Setup localization for page creation dialog
gettext.find("PageDlg")
translate = gettext.translation('PageDlg', localedir='locale', languages=[get_language()], fallback=True)
translate.install()
_ = translate.gettext


class PageDlg(QDialog):
    """Dialog allowing users to choose orientation, paper size, and border style for a new page."""

    def __init__(self, parent=None):
        super(PageDlg, self).__init__(parent)
        self.setWindowTitle(_("Create new Page"))
        self.pageType = "portrait"

        # Dynamically resolve application and image asset directories
        self.base_dir = self._get_app_dir()
        self.images_dir = self._get_resource_dir("Images")

        # Load initial configuration values
        self.borderStyle = self.get_configured_border_style()
        self.paperFormat = self.get_configured_paper_format()
        self.createDlg()

    def _get_app_dir(self) -> Path:
        """Determine root application directory across packaged executables and source runs."""
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).resolve().parent
        else:
            script_dir = Path(__file__).resolve().parent
            parent_dir = script_dir.parent

            if any((parent_dir / folder).exists() for folder in ["Databases", "Images", "Photos", "docs", "Help", "locale"]):
                return parent_dir

            return script_dir

    def _get_resource_dir(self, folder_name: str) -> Path:
        """Resolve absolute path to a specific resource directory."""
        res_dir = self.base_dir / folder_name
        if res_dir.exists():
            return res_dir
        return Path(__file__).resolve().parent / folder_name

    def _get_pixmap(self, image_filename: str) -> QPixmap:
        """Safely load a QPixmap from the resolved Images directory."""
        image_path = self.images_dir / image_filename
        if image_path.exists():
            return QPixmap(str(image_path))
        return QPixmap(f"../Images/{image_filename}")

    def get_configured_border_style(self) -> str:
        """Retrieve default border style setting from configuration file."""
        return get_config_value('type encadrement', PageBorder.STYLE_TRIPLE)

    def get_configured_paper_format(self) -> str:
        """Retrieve default paper format setting from configuration file."""
        return get_config_value('paper format', "A4")

    def createDlg(self):
        """Construct dialog widgets, layouts, and input controls."""
        # Page preview thumbnail
        self.photo = QLabel()
        self.photo.setFixedHeight(100)
        self.photo.setFixedWidth(200)
        self.photo.setPixmap(self._get_pixmap("portrait.png"))

        # Orientation selection radio buttons
        rbtn1 = QRadioButton(_('Portrait'))
        rbtn2 = QRadioButton(_('Landscape'))

        rbtn1.setChecked(True)

        rbtn1.clicked.connect(self.rbtn1Clicked)
        rbtn2.clicked.connect(self.rbtn2Clicked)

        rbGroup = QGroupBox(_("Select the page:"))
        vbox = QVBoxLayout()
        hBox = QHBoxLayout()
        rbGroup.setLayout(hBox)

        vbox.addWidget(rbtn1)
        vbox.addWidget(rbtn2)

        hBox.addLayout(vbox)
        hBox.addWidget(self.photo)

        # Paper format selector dropdown
        self.paperFormatCombo = QComboBox()
        self.paperFormatCombo.addItem("A4", "A4")
        self.paperFormatCombo.addItem("Letter", "Letter")

        idx_format = self.paperFormatCombo.findData(self.paperFormat)
        if idx_format != -1:
            self.paperFormatCombo.setCurrentIndex(idx_format)

        self.paperFormatCombo.currentIndexChanged.connect(self.onPaperFormatChanged)

        # Border style selector dropdown
        self.borderStyleCombo = QComboBox()
        self.borderStyleCombo.addItem(_("Triple (Classic)"), PageBorder.STYLE_TRIPLE)
        self.borderStyleCombo.addItem(_("Simple (Frame)"), PageBorder.STYLE_SIMPLE)
        self.borderStyleCombo.addItem(_("Greek (Notched)"), PageBorder.STYLE_GREEK)
        self.borderStyleCombo.addItem(_("Dentelle (Philately)"), PageBorder.STYLE_DENTELLE)

        # Preselect configured border style
        idx_border = self.borderStyleCombo.findData(self.borderStyle)
        if idx_border != -1:
            self.borderStyleCombo.setCurrentIndex(idx_border)

        self.borderStyleCombo.currentIndexChanged.connect(self.onBorderStyleChanged)

        # Form layout for dropdown configurations
        fLayout = QFormLayout()
        fLayout.addRow(_("Paper format:"), self.paperFormatCombo)
        fLayout.addRow(_("Border type:"), self.borderStyleCombo)

        # Main layout assembly
        vLayout1 = QVBoxLayout()
        vLayout1.addWidget(rbGroup)
        vLayout1.addLayout(fLayout)

        # Standard dialog action buttons
        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                              QDialogButtonBox.StandardButton.Cancel)

        # Explicit button label translations
        ok_button = bb.button(QDialogButtonBox.StandardButton.Ok)
        if ok_button:
            ok_button.setText(_("OK"))

        cancel_button = bb.button(QDialogButtonBox.StandardButton.Cancel)
        if cancel_button:
            cancel_button.setText(_("Cancel"))

        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        vLayout1.addWidget(bb)
        self.setLayout(vLayout1)

    def rbtn1Clicked(self):
        """Update orientation to portrait and display matching preview icon."""
        self.photo.setPixmap(self._get_pixmap("portrait.png"))
        self.pageType = "portrait"

    def rbtn2Clicked(self):
        """Update orientation to landscape and display matching preview icon."""
        self.photo.setPixmap(self._get_pixmap("landscape.png"))
        self.pageType = "landscape"

    def onBorderStyleChanged(self, index):
        """Update current border style selection from dropdown item data."""
        self.borderStyle = self.borderStyleCombo.currentData()

    def onPaperFormatChanged(self, index):
        """Update current paper format selection from dropdown item data."""
        self.paperFormat = self.paperFormatCombo.currentData()