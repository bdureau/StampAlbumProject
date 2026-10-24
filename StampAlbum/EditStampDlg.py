from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMessageBox, QFileDialog, QLabel, QHBoxLayout,
    QDialog, QPushButton, QListWidget, QLineEdit,
    QFormLayout, QVBoxLayout, QDialogButtonBox, QPlainTextEdit
)
from PyQt6.QtGui import QPixmap, QDragEnterEvent, QDropEvent
from Databases import DB
from SAAppPaths import list_countries

import gettext
from AppLanguage import get_language
gettext.find("EditStampDlg")
translate = gettext.translation('EditStampDlg', localedir='locale', languages=[get_language()], fallback=True)
translate.install()
_ = translate.gettext


class DropImageLabel(QLabel):
    """Custom QLabel that supports image file drag and drop operations."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.parent_dialog = parent

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Accept drag event if it contains supported local image file URLs."""
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                ext = Path(url.toLocalFile()).suffix.lower()
                if ext in [".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"]:
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event: QDropEvent):
        """Extract dropped image path and pass it to the parent dialog."""
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path and self.parent_dialog is not None:
                self.parent_dialog.set_image_from_path(file_path)
                event.acceptProposedAction()
                return
        event.ignore()


class EditStampDlg(QDialog):
    """Dialog allowing users to edit attributes and image of an existing stamp."""

    def __init__(self, stampObj, parent=None):
        super(EditStampDlg, self).__init__(parent)
        self.setWindowTitle(_("Edit stamp"))
        self.createDlg(stampObj)

    def createDlg(self, stampObj):
        self.eTitle = QPlainTextEdit()
        self.eTitle.setPlainText(stampObj['stampDesc_text'])
        self.eTitle.setFixedHeight(50)

        self.eNbr = QLineEdit()
        self.eNbr.setText(stampObj['stampNbr_text'])

        self.eValue = QPlainTextEdit()
        self.eValue.setPlainText(stampObj['stampValue_text'])
        self.eValue.setFixedHeight(30)

        # Image preview label with Drag and Drop support
        self.photo = DropImageLabel(self)
        self.photo.setFixedHeight(200)
        self.photo.setFixedWidth(200)
        self.photo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.photo.setStyleSheet("border: 2px dashed #999; background: #fafafa;")

        # Keep full-resolution pixmap in memory to avoid degrading quality through the 200px thumbnail preview
        self.fullPixmap = stampObj.get('pixmapItem_image')
        if not isinstance(self.fullPixmap, QPixmap):
            self.fullPixmap = QPixmap()
        self._showPreview(self.fullPixmap)

        # Manual image browse button
        imageButton = QPushButton(_("&Change image ..."))
        buttonBox = QDialogButtonBox(Qt.Orientation.Horizontal)
        buttonBox.addButton(imageButton, QDialogButtonBox.ButtonRole.ActionRole)
        imageButton.clicked.connect(self.loadImage)

        # OK and Cancel standard dialog buttons
        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)

        # Translate buttons
        ok_btn = bb.button(QDialogButtonBox.StandardButton.Ok)
        if ok_btn:
            ok_btn.setText(_("OK"))

        cancel_btn = bb.button(QDialogButtonBox.StandardButton.Cancel)
        if cancel_btn:
            cancel_btn.setText(_("Cancel"))

        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)

        # Right form layout
        flo = QFormLayout()
        flo.addRow(_("Title:"), self.eTitle)
        flo.addRow(_("Nbr"), self.eNbr)
        flo.addRow(_("Value"), self.eValue)
        flo.addRow(self.photo)
        flo.addRow(buttonBox)
        flo.addRow(bb)

        # Left mount box list layout
        vLayout1 = QVBoxLayout()
        pochettesType = QLabel(_("Pochette type"))
        self.pochetteList = QListWidget()
        self.pochetteList.setMaximumWidth(150)
        vLayout1.addWidget(pochettesType)
        vLayout1.addWidget(self.pochetteList)

        # Main horizontal layout
        hLayout2 = QHBoxLayout()
        hLayout2.addLayout(vLayout1)
        hLayout2.addLayout(flo)

        self.setLayout(hLayout2)
        self.populateData(stampObj)

    def populateData(self, stampObj):
        """Populate mount box list and select the stamp's current box."""
        self.db = None
        # Retrieve country database list according to configured engine (.db or .mdb)
        self.stampCountries = list_countries()

        # Only the master database is needed here to load mount box types
        if self.stampCountries:
            try:
                self.db = DB(self.stampCountries[0])
            except Exception as e:
                QMessageBox.critical(self, _("Database error"), str(e))
                self.db = None

        if self.db is None:
            return

        # Load available mount boxes from the master DB
        retBoxList = self.db.loadBoxList()
        self.pochetteList.clear()
        self.pochetteList.addItems(retBoxList)

        retPochette = "Pochette " + str(stampObj['stampBox_boxWidth']) + "x" + str(stampObj['stampBox_boxHeight'])
        if len(retPochette) > 0:
            pochetteItem = self.pochetteList.findItems(retPochette, Qt.MatchFlag.MatchExactly)

            if len(pochetteItem) > 0:
                self.pochetteList.setCurrentItem(pochetteItem[0])
            else:
                self.pochetteList.setCurrentRow(0)

    def getBoxInfo(self, box):
        """Retrieve box dimensions from the active database."""
        ret = []
        if self.db is not None:
            ret = self.db.getCurrentBox(box)
        return ret

    def _showPreview(self, pix):
        """Scale and display pixmap thumbnail inside the preview label."""
        if pix is None or pix.isNull():
            return
        if pix.width() > pix.height():
            self.photo.setPixmap(pix.scaledToWidth(200, Qt.TransformationMode.SmoothTransformation))
        else:
            self.photo.setPixmap(pix.scaledToHeight(200, Qt.TransformationMode.SmoothTransformation))

    def getPixmap(self):
        """Return the full-resolution QPixmap to assign to the stamp object."""
        return self.fullPixmap

    def set_image_from_path(self, file_path: str):
        """Load an image from a given file path and update the preview."""
        pix = QPixmap(file_path)
        if not pix.isNull():
            self.fullPixmap = pix
            self._showPreview(pix)

    def loadImage(self):
        """Open a file dialog to select and load an image manually."""
        options = QFileDialog.Option.DontUseNativeDialog
        fileName, _filter = QFileDialog.getOpenFileName(
            self, _("Select picture"), "",
            _("all pictures (*.jpg *.jpeg *.png);;PNG (*.png)"),
            options=options
        )
        if fileName:
            self.set_image_from_path(fileName)

    def changeFont(self):
        print("change font")