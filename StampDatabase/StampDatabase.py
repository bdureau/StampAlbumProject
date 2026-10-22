"""
StampDatabase Application
-------------------------
A standalone desktop database administration application for managing
country-specific stamp catalogues used by StampAlbum and StampCatalogue.

Supports SQLite and MS Access Databases, CSV import/export (comma default),
Undo/Redo, full record editing, add/delete records, MS Access availability verification,
MS Access to SQLite database conversion, and metadata inspection.

Author: Boris du Reau
Year: 2026
"""

import sys
import csv
import sqlite3
import configparser
from pathlib import Path
from PyQt6 import QtGui
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QLabel, QTableWidget, QTableWidgetItem, QPushButton,
    QHeaderView, QLineEdit, QMessageBox,
    QFileDialog, QGroupBox, QFormLayout, QTextEdit, QSplitter,
    QDialog, QDialogButtonBox, QRadioButton, QToolBar
)
from PyQt6.QtGui import QPixmap, QKeySequence, QDesktopServices, QUndoStack, QUndoCommand, QIcon, QAction

from SDAboutDlg import SDAboutDlg

# Try importing pyodbc for Microsoft Access support
try:
    import pyodbc

    HAS_PYODBC = True
except ImportError:
    HAS_PYODBC = False

# Localization setup matching StampAlbum architecture
import gettext
from SDAppLanguage import get_language

gettext.find("StampDatabase")
translate = gettext.translation(
    'StampDatabase', localedir='locale', languages=[get_language()], fallback=True
)
translate.install()
_ = translate.gettext


def test_ms_access_support() -> bool:
    """Check if pyodbc module is loaded and MS Access ODBC drivers are functional."""
    if not HAS_PYODBC:
        return False
    try:
        drivers = pyodbc.drivers()
        return any("Microsoft Access Driver" in driver for driver in drivers)
    except Exception:
        return False

class AppConfigManager:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config = configparser.ConfigParser()
        self.language = "fr"
        self.db_type = "sqlite"
        self.last_country = ""
        self.load_config()

    def load_config(self):
        if self.config_path.exists():
            self.config.read(self.config_path, encoding='utf-8')
            if 'General' in self.config:
                self.language = self.config['General'].get('language', 'fr')
                self.db_type = self.config['General'].get('db_type', 'sqlite')
                self.last_country = self.config['General'].get('last_country', '')

    def save_config(self, language=None, db_type=None, last_country=None):
        if language is not None: self.language = language
        if db_type is not None: self.db_type = db_type
        if last_country is not None: self.last_country = last_country

        if 'General' not in self.config:
            self.config['General'] = {}

        self.config['General']['language'] = self.language
        self.config['General']['db_type'] = self.db_type
        self.config['General']['last_country'] = self.last_country

        with open(self.config_path, 'w', encoding='utf-8') as f:
            self.config.write(f)

class UpdateStampCommand(QUndoCommand):
    """QUndoCommand implementation for stamp record modifications."""

    def __init__(self, main_window, stamp_key, old_data, new_data, description="Update Stamp Record"):
        super().__init__(description)
        self.main_window = main_window
        self.stamp_key = stamp_key
        self.old_data = old_data
        self.new_data = new_data

    def undo(self):
        self.main_window.apply_stamp_data(self.stamp_key, self.old_data)

    def redo(self):
        self.main_window.apply_stamp_data(self.stamp_key, self.new_data)


class AddStampCommand(QUndoCommand):
    """QUndoCommand implementation for adding a new stamp record."""

    def __init__(self, main_window, stamp_data, description="Add Stamp Record"):
        super().__init__(description)
        self.main_window = main_window
        self.stamp_data = stamp_data
        self.stamp_key = stamp_data[0]

    def undo(self):
        self.main_window.db_adapter.delete_stamp(self.stamp_key)
        self.main_window._refresh_table()

    def redo(self):
        self.main_window.db_adapter.insert_stamp(self.stamp_data)
        self.main_window._refresh_table()
        # Sélectionner et faire défiler jusqu'au nouveau timbre inséré
        self.main_window._select_stamp_by_key_or_nbr(self.stamp_key, self.stamp_data[1])

class DeleteStampsCommand(QUndoCommand):
    """QUndoCommand implementation for deleting one or multiple stamp records."""

    def __init__(self, main_window, stamps_list, description="Delete Stamp Record(s)"):
        super().__init__(description)
        self.main_window = main_window
        self.stamps_list = stamps_list

    def undo(self):
        for stamp_data in self.stamps_list:
            self.main_window.db_adapter.insert_stamp(stamp_data)
        self.main_window._refresh_table()

    def redo(self):
        for stamp_data in self.stamps_list:
            stamp_key = stamp_data[0]
            self.main_window.db_adapter.delete_stamp(stamp_key)
        self.main_window._refresh_table()


class CountryDatabaseAdapter:
    """Handles read/write operations for country Databases (SQLite or MS Access)."""

    DB_INFO_COLUMNS = ["Author", "Country", "Description", "Version", "Catalogue", "Language"]

    def __init__(self, country: str, db_dir: Path, db_type: str = "sqlite"):
        self.country = country
        self.db_dir = db_dir
        self.db_type = db_type.lower()
        self.conn = None
        self.cursor = None

        self._connect()
        self.ensure_db_schema()

    def _connect(self):
        """Establish database connection based on type."""
        if self.db_type == "sqlite":
            db_path = self.db_dir / f"{self.country}.db"
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
        else:
            if not test_ms_access_support():
                raise RuntimeError("MS Access support is unavailable or drivers are missing.")
            db_path = self.db_dir / f"{self.country}.mdb"
            conn_str = f"Driver={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path};"
            self.conn = pyodbc.connect(conn_str)
            self.cursor = self.conn.cursor()

    def execute_query(self, query: str, params: tuple = ()):
        """Execute parameterized query."""
        self.cursor.execute(query, params)
        return self.cursor

    def ensure_db_schema(self):
        """Ensure Stamp_List and db_info tables exist for a functional database."""
        if self.db_type == "sqlite":
            self.execute_query("""
                CREATE TABLE IF NOT EXISTS Stamp_List (
                    key TEXT PRIMARY KEY,
                    nbr TEXT,
                    year TEXT,
                    type TEXT,
                    valuecolor TEXT,
                    stampDescription1 TEXT,
                    stampDescription TEXT,
                    width TEXT,
                    height TEXT,
                    sequence TEXT,
                    ascii_seq TEXT,
                    sub_nbr TEXT
                )
            """)

        existing_cols = self.get_db_info_existing_columns()
        if existing_cols is None:
            if self.db_type == "sqlite":
                self.execute_query("""
                    CREATE TABLE IF NOT EXISTS db_info (
                        Author TEXT,
                        Country TEXT,
                        Description TEXT,
                        Version TEXT,
                        Catalogue TEXT,
                        Language TEXT
                    )
                """)
                self.execute_query("""
                    INSERT INTO db_info (Author, Country, Description, Version, Catalogue, Language)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, ("Boris du Reau", self.country, f"{self.country} Stamp Catalogue", "1.0", "Yvert", "fr"))
                self.commit()

    def get_db_info_existing_columns(self):
        """Return existing column names for db_info, or None if table does not exist."""
        try:
            if self.db_type == "sqlite":
                res = self.execute_query("PRAGMA table_info(db_info)")
                rows = res.fetchall()
                if not rows:
                    return None
                return [row[1] for row in rows]
            else:
                res = self.execute_query("SELECT * FROM db_info WHERE 1=0")
                return [column[0] for column in res.description]
        except Exception:
            return None

    def get_db_info(self):
        """Fetch metadata dictionary and missing column list for db_info."""
        existing_cols = self.get_db_info_existing_columns()
        if not existing_cols:
            return {}, list(self.DB_INFO_COLUMNS)

        missing_cols = [c for c in self.DB_INFO_COLUMNS if c not in existing_cols]
        valid_cols = [c for c in self.DB_INFO_COLUMNS if c in existing_cols]

        if not valid_cols:
            return {}, list(self.DB_INFO_COLUMNS)

        query = f"SELECT {', '.join(valid_cols)} FROM db_info"
        try:
            res = self.execute_query(query)
            row = res.fetchone()
            if row:
                info_data = dict(zip(valid_cols, row))
            else:
                info_data = {}
        except Exception:
            info_data = {}

        return info_data, missing_cols

    def update_db_info(self, info_dict):
        """Update existing db_info columns."""
        existing_cols = self.get_db_info_existing_columns()
        if not existing_cols:
            return

        valid_updates = {k: v for k, v in info_dict.items() if k in existing_cols}
        if not valid_updates:
            return

        res = self.execute_query("SELECT COUNT(*) FROM db_info")
        count = res.fetchone()[0]

        if count == 0:
            cols = list(valid_updates.keys())
            vals = list(valid_updates.values())
            placeholders = ", ".join(["?"] * len(vals))
            query = f"INSERT INTO db_info ({', '.join(cols)}) VALUES ({placeholders})"
            self.execute_query(query, tuple(vals))
        else:
            set_clause = ", ".join([f"{k} = ?" for k in valid_updates.keys()])
            vals = list(valid_updates.values())
            query = f"UPDATE db_info SET {set_clause}"
            self.execute_query(query, tuple(vals))

        self.commit()

    def load_types(self):
        """Fetch distinct stamp categories."""
        res = self.execute_query("SELECT DISTINCT type FROM Stamp_List WHERE type IS NOT NULL ORDER BY type ASC")
        return [row[0] for row in res.fetchall() if row[0] is not None]

    def load_years(self):
        """Fetch distinct issue years."""
        res = self.execute_query("SELECT DISTINCT year FROM Stamp_List WHERE year IS NOT NULL ORDER BY year ASC")
        return [row[0] for row in res.fetchall() if row[0] is not None]

    def get_stamps(self, stamp_type=None, year=None, search_nbr=None):
        """Query catalogue stamps based on filters (Ordre: description1 puis description)."""
        query = """
            SELECT key, nbr, year, type, valuecolor, stampDescription1, stampDescription, width, height, sequence, ascii_seq, sub_nbr
            FROM Stamp_List
            WHERE 1=1
        """
        params = []

        if stamp_type and stamp_type != _("All"):
            query += " AND type = ?"
            params.append(stamp_type)

        if year and year != _("All"):
            query += " AND year = ?"
            params.append(str(year))

        if search_nbr:
            query += " AND nbr LIKE ?"
            params.append(f"%{search_nbr}%")

        query += " ORDER BY sequence, ascii_seq, nbr ASC"
        res = self.execute_query(query, tuple(params))
        return res.fetchall()

    def update_stamp(self, key, nbr, year, stype, valcolor, desc1, desc, width, height, sequence, ascii_seq, sub_nbr):
        """Update an existing stamp record in catalogue."""
        query = """
            UPDATE Stamp_List
            SET nbr = ?, year = ?, type = ?, valuecolor = ?, stampDescription1 = ?, stampDescription = ?, width = ?, height = ?, sequence = ?, ascii_seq = ?, sub_nbr = ?
            WHERE key = ?
        """
        self.execute_query(query, (
            str(nbr), str(year), str(stype), str(valcolor), str(desc1), str(desc), str(width), str(height), str(sequence),
            str(ascii_seq), str(sub_nbr), key))

    def insert_stamp(self, stamp_data):
        """Insert a new stamp record into catalogue."""
        key, nbr, year, stype, valcolor, desc1, desc, width, height, sequence, ascii_seq, sub_nbr = stamp_data
        query = """
            INSERT INTO Stamp_List (key, nbr, year, type, valuecolor, stampDescription1, stampDescription, width, height, sequence, ascii_seq, sub_nbr)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.execute_query(query, (
            str(key), str(nbr), str(year), str(stype), str(valcolor), str(desc1), str(desc), str(width), str(height), str(sequence),
            str(ascii_seq), str(sub_nbr)))

    def delete_stamp(self, key):
        """Delete a stamp record by key."""
        query = "DELETE FROM Stamp_List WHERE key = ?"
        self.execute_query(query, (str(key),))

    def key_exists(self, key):
        """Check if a primary key already exists in Stamp_List."""
        res = self.execute_query("SELECT COUNT(*) FROM Stamp_List WHERE key = ?", (str(key),))
        return res.fetchone()[0] > 0

    def get_max_key(self):
        """Get max integer key from Stamp_List to generate new unique key."""
        res = self.execute_query("SELECT MAX(CAST(key AS INTEGER)) FROM Stamp_List")
        row = res.fetchone()
        if row and row[0] is not None:
            return int(row[0])
        return 0

    def commit(self):
        """Commit changes to database."""
        if self.conn:
            self.conn.commit()

    def close(self):
        """Close connection."""
        if self.conn:
            self.conn.close()


class DatabaseInfoDialog(QDialog):
    """Dialog displaying and editing db_info database metadata."""

    def __init__(self, db_adapter, country_name, parent=None):
        super().__init__(parent)
        self.db_adapter = db_adapter
        self.setWindowTitle(_("Database Information") + f" - {country_name}")
        self.resize(450, 320)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.info_data, self.missing_cols = db_adapter.get_db_info()

        form.addRow(_("Database Name:"), QLabel(f"<b>{country_name}</b>"))
        form.addRow(_("Database Type:"), QLabel(db_adapter.db_type.upper()))

        self.fields = {}

        self.fields["Author"] = QLineEdit(self.info_data.get("Author", ""))
        form.addRow(_("Author:"), self.fields["Author"])

        self.fields["Country"] = QLineEdit(self.info_data.get("Country", country_name))
        form.addRow(_("Country:"), self.fields["Country"])

        self.fields["Description"] = QTextEdit()
        self.fields["Description"].setPlainText(self.info_data.get("Description", ""))
        self.fields["Description"].setMaximumHeight(60)
        form.addRow(_("Description:"), self.fields["Description"])

        self.fields["Version"] = QLineEdit(self.info_data.get("Version", "1.0"))
        form.addRow(_("Version:"), self.fields["Version"])

        self.combo_catalogue = QComboBox()
        self.combo_catalogue.setEditable(True)
        self.combo_catalogue.addItems(["Yvert", "Philatelix", "Scott", "Michel", "Stanley Gibbons", "Custom"])
        self.combo_catalogue.setCurrentText(self.info_data.get("catalogue", "Yvert"))
        form.addRow(_("Catalogue System:"), self.combo_catalogue)

        self.combo_language = QComboBox()
        self.combo_language.addItem(_("French"), "fr")
        self.combo_language.addItem(_("English"), "en")
        lang_val = self.info_data.get("Language", "fr")
        idx = self.combo_language.findData(lang_val)
        if idx != -1:
            self.combo_language.setCurrentIndex(idx)
        else:
            self.combo_language.setCurrentText(lang_val)
        form.addRow(_("Data Language:"), self.combo_language)

        for col in self.missing_cols:
            if col in self.fields:
                self.fields[col].setEnabled(False)
                self.fields[col].setToolTip(_("Column missing in database db_info table."))
            elif col == "Catalogue":
                self.combo_catalogue.setEnabled(False)
            elif col == "Language":
                self.combo_language.setEnabled(False)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.save_info)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def save_info(self):
        """Save form modifications back to db_info table."""
        updated_dict = {
            "Author": self.fields["Author"].text().strip(),
            "Country": self.fields["Country"].text().strip(),
            "Description": self.fields["Description"].toPlainText().strip(),
            "Version": self.fields["Version"].text().strip(),
            "Catalogue": self.combo_catalogue.currentText().strip(),
            "Language": self.combo_language.currentData() or self.combo_language.currentText().strip()
        }
        self.db_adapter.update_db_info(updated_dict)
        self.accept()


class CreateDatabaseDialog(QDialog):
    """Dialog to create a new empty SQLite database."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Create New Empty SQLite Database"))
        self.resize(380, 220)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.edit_country = QLineEdit()
        self.edit_country.setPlaceholderText(_("e.g. Monaco, Belgium..."))

        self.edit_author = QLineEdit("Boris du Reau")
        self.edit_desc = QLineEdit()
        self.combo_catalogue = QComboBox()
        self.combo_catalogue.setEditable(True)
        self.combo_catalogue.addItems(["Yvert", "Philatelix", "Scott", "Michel", "Stanley Gibbons"])

        self.combo_language = QComboBox()
        self.combo_language.addItem("Français", "fr")
        self.combo_language.addItem("English", "en")

        form.addRow(_("Country / DB Name:"), self.edit_country)
        form.addRow(_("Author:"), self.edit_author)
        form.addRow(_("Description:"), self.edit_desc)
        form.addRow(_("Catalogue System:"), self.combo_catalogue)
        form.addRow(_("Data Language:"), self.combo_language)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
        return {
            "country": self.edit_country.text().strip(),
            "author": self.edit_author.text().strip(),
            "description": self.edit_desc.text().strip(),
            "catalogue": self.combo_catalogue.currentText().strip(),
            "language": self.combo_language.currentData()
        }


class CsvDelimiterDialog(QDialog):
    """Dialog to select delimiter for CSV Import/Export (Comma selected by default)."""

    def __init__(self, parent=None, title="CSV Delimiter"):
        super().__init__(parent)
        self.setWindowTitle(_(title))
        self.resize(300, 120)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(_("Select CSV Delimiter:")))

        self.radio_comma = QRadioButton(_("Comma ( , )"))
        self.radio_semicolon = QRadioButton(_("Semicolon ( ; )"))
        self.radio_comma.setChecked(True)

        layout.addWidget(self.radio_comma)
        layout.addWidget(self.radio_semicolon)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_delimiter(self):
        return "," if self.radio_comma.isChecked() else ";"


class ConfigDialog(QDialog):
    """Configuration dialog for language and database preferences."""

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle(_("Application Configuration"))
        self.resize(350, 150)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.combo_lang = QComboBox()
        self.combo_lang.addItem("English", "en")
        self.combo_lang.addItem("Français", "fr")

        # Sélectionner la langue actuelle dans la combo box
        idx_lang = self.combo_lang.findData(self.config_manager.language)
        if idx_lang != -1:
            self.combo_lang.setCurrentIndex(idx_lang)

        self.combo_db_type = QComboBox()
        self.combo_db_type.addItem("SQLite", "sqlite")
        self.combo_db_type.addItem("Microsoft Access", "access")

        # Sélectionner le type de base de données actuel dans la combo box
        idx_db = self.combo_db_type.findData(self.config_manager.db_type)
        if idx_db != -1:
            self.combo_db_type.setCurrentIndex(idx_db)

        form.addRow(_("Language:"), self.combo_lang)
        form.addRow(_("Database Type:"), self.combo_db_type)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_selected_config(self):
        """Retourne les valeurs sélectionnées dans la boîte de dialogue."""
        return {
            "language": self.combo_lang.currentData(),
            "db_type": self.combo_db_type.currentData()
        }


class MainWindow(QMainWindow):
    """Main Window for StampDatabase administration tool."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(_("StampDatabase - Stamp Catalogue Administrator"))
        self.resize(1300, 850)

        self.base_dir = self._get_app_dir()
        self.db_dir = self.base_dir / "Databases"
        self.config_manager = AppConfigManager(self.base_dir / "StampDatabase.cfg")
        self.current_db_type = self.config_manager.db_type
        self.db_adapter = None
        self.current_country = None
        self.is_dirty = False

        self.images_dir = self.base_dir / "Images"

        icon_path = self.images_dir / "StampDB.png"
        if icon_path.exists():
            self.setWindowIcon(QtGui.QIcon(str(icon_path)))
        else:
            self.setWindowIcon(QtGui.QIcon('StampDB.png'))

        self.undo_stack = QUndoStack(self)
        self.undo_stack.cleanChanged.connect(self._update_dirty_state)

        self.available_countries = self._detect_available_countries()

        self._init_ui()
        self._init_menubar()
        self._init_toolbar()
        self._load_country_list()

    def _get_app_dir(self) -> Path:
        """Détermine le répertoire racine de l'application."""
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).resolve().parent
        else:
            script_dir = Path(__file__).resolve().parent
            parent_dir = script_dir.parent
            if any((parent_dir / folder).exists() for folder in ["Databases", "Images", "Photos"]):
                return parent_dir
            return script_dir

    def _detect_available_countries(self):
        """Detect country Databases in Databases/ folder."""
        if not self.db_dir.exists():
            return []
        ext = ".db" if self.current_db_type == "sqlite" else ".mdb"
        return sorted([f.stem for f in self.db_dir.glob(f"*{ext}") if f.stem not in ["master", "collections"]])

    def show_access_warning_popup(self):
        """Display warning popup when MS Access is not configured or fails to initialize."""
        QMessageBox.warning(
            self,
            _("MS Access Configuration Error"),
            _("<b>Microsoft Access is not configured properly or drivers are missing.</b><br><br>"
              "Please refer to the application documentation to install the required "
              "64-bit ODBC Access drivers (<code>accessdatabaseengine_X64.exe /quiet</code>).<br><br>"
              "MS Access features have been disabled. The application will revert to SQLite mode.")
        )

    def _init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # Country Header Bar
        country_box = QGroupBox(_("Database Selection"))
        country_layout = QHBoxLayout()

        country_layout.addWidget(QLabel(_("Active Country Database:")))
        self.combo_country = QComboBox()
        self.combo_country.currentIndexChanged.connect(self._on_country_changed)
        country_layout.addWidget(self.combo_country, stretch=1)
        country_layout.addStretch(2)

        country_box.setLayout(country_layout)
        main_layout.addWidget(country_box)

        # Filter Bar
        filter_box = QGroupBox(_("Catalogue Filters"))
        filter_layout = QHBoxLayout()

        filter_layout.addWidget(QLabel(_("Type:")))
        self.combo_type = QComboBox()
        self.combo_type.setMinimumWidth(250)
        self.combo_type.currentTextChanged.connect(self._refresh_table)
        filter_layout.addWidget(self.combo_type, stretch=3)

        filter_layout.addWidget(QLabel(_("Year:")))
        self.combo_year = QComboBox()
        self.combo_year.currentTextChanged.connect(self._refresh_table)
        filter_layout.addWidget(self.combo_year, stretch=1)

        filter_layout.addWidget(QLabel(_("Catalog N°:")))
        self.edit_search_nbr = QLineEdit()
        self.edit_search_nbr.setPlaceholderText(_("e.g. 154..."))
        self.edit_search_nbr.setMaxLength(10)
        self.edit_search_nbr.setMaximumWidth(100)
        self.edit_search_nbr.textChanged.connect(self._refresh_table)
        filter_layout.addWidget(self.edit_search_nbr, stretch=1)

        filter_box.setLayout(filter_layout)
        main_layout.addWidget(filter_box)

        # Main Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Stamps Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            _("Yvert N°"),
            _("Year"),
            _("Type"),
            _("Value / Color"),
            _("Description 1"),
            _("Description")
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)

        self.table.setSortingEnabled(True)

        self.table.itemSelectionChanged.connect(self._on_stamp_selected)
        splitter.addWidget(self.table)

        # Right Panel (Details Editor + Photo Viewer + Add/Delete Record Buttons)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Image Viewer
        self.img_label = QLabel(_("No Photo Available"))
        self.img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_label.setFixedSize(200, 200)
        self.img_label.setStyleSheet("border: 1px solid #cbd5e0; background: #f7fafc;")
        right_layout.addWidget(self.img_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Stamp Record Editor Box
        editor_box = QGroupBox(_("Stamp Catalogue Record Editor"))
        form = QFormLayout()

        self.edit_nbr = QLineEdit()
        self.edit_sub_nbr = QLineEdit()
        self.edit_year = QLineEdit()
        #self.edit_type = QLineEdit()
        self.edit_type = QComboBox()
        self.edit_type.setEditable(True)
        self.edit_valcolor = QLineEdit()

        self.edit_desc1 = QTextEdit()
        self.edit_desc1.setMaximumHeight(50)
        self.edit_desc = QTextEdit()
        self.edit_desc.setMaximumHeight(50)

        self.edit_width = QLineEdit()
        self.edit_height = QLineEdit()

        self.edit_sequence = QLineEdit()
        self.edit_sequence.setReadOnly(True)
        self.edit_sequence.setStyleSheet("background-color: #edf2f7; color: #718096;")

        self.edit_ascii_seq = QLineEdit()
        self.edit_ascii_seq.setReadOnly(True)
        self.edit_ascii_seq.setStyleSheet("background-color: #edf2f7; color: #718096;")

        form.addRow(_("Yvert N°:"), self.edit_nbr)
        form.addRow(_("Sub N° / Variant:"), self.edit_sub_nbr)
        form.addRow(_("Year:"), self.edit_year)
        form.addRow(_("Category / Type:"), self.edit_type)
        form.addRow(_("Value / Color:"), self.edit_valcolor)
        form.addRow(_("Description 1:"), self.edit_desc1)
        form.addRow(_("Description:"), self.edit_desc)
        form.addRow(_("Width (mm):"), self.edit_width)
        form.addRow(_("Height (mm):"), self.edit_height)
        form.addRow(_("Sequence:"), self.edit_sequence)
        form.addRow(_("ASCII Sequence:"), self.edit_ascii_seq)

        btn_apply = QPushButton(_("Apply Record Modification"))
        btn_apply.setStyleSheet("background-color: #1d6f42; color: white; font-weight: bold;")
        btn_apply.clicked.connect(self._on_apply_record_edit)
        form.addRow(btn_apply)

        editor_box.setLayout(form)
        right_layout.addWidget(editor_box)

        # Action Buttons: Add Record / Delete Record
        btn_layout = QHBoxLayout()

        btn_add = QPushButton(_("Add Stamp Record"))
        btn_add.setStyleSheet("background-color: #2b6cb0; color: white; font-weight: bold;")
        btn_add.clicked.connect(self._on_add_stamp_record)
        btn_layout.addWidget(btn_add)

        btn_delete = QPushButton(_("Delete Stamp Record(s)"))
        btn_delete.setStyleSheet("background-color: #c53030; color: white; font-weight: bold;")
        btn_delete.clicked.connect(self._on_delete_stamp_record)
        btn_layout.addWidget(btn_delete)

        right_layout.addLayout(btn_layout)

        splitter.addWidget(right_panel)
        splitter.setSizes([650, 450])

        main_layout.addWidget(splitter)

    def _init_menubar(self):
        """Initialize main menu bar with explicit actions."""
        menubar = self.menuBar()

        # File / Database Menu
        file_menu = menubar.addMenu(_("&File"))

        self.act_create_db = QAction(_("Create New Empty SQLite DB..."), self)
        self.act_create_db.setIcon(QIcon(str(self.base_dir / "Images" / "database_add.png")))
        self.act_create_db.triggered.connect(self.create_new_sqlite_db)
        file_menu.addAction(self.act_create_db)

        self.act_save_db = QAction(_("Save Changes"), self)
        self.act_save_db.setIcon(QIcon(str(self.base_dir / "Images" / "save.png")))
        self.act_save_db.setShortcut(QKeySequence.StandardKey.Save)
        self.act_save_db.triggered.connect(self.save_changes)
        file_menu.addAction(self.act_save_db)

        file_menu.addSeparator()

        self.act_db_info = QAction(_("Current Database Info..."), self)
        self.act_db_info.triggered.connect(self.open_db_info)
        file_menu.addAction(self.act_db_info)

        file_menu.addSeparator()

        self.act_convert_access = QAction(_("Import MS Access DB to SQLite..."), self)
        self.act_convert_access.triggered.connect(self.import_ms_access_to_sqlite)
        file_menu.addAction(self.act_convert_access)

        self.act_import_csv = QAction(_("Import CSV..."), self)
        self.act_import_csv.setIcon(QIcon(str(self.base_dir / "Images" / "import_csv.png")))
        self.act_import_csv.triggered.connect(self.import_csv)
        file_menu.addAction(self.act_import_csv)

        self.act_export_csv = QAction(_("Export CSV..."), self)
        self.act_export_csv.setIcon(QIcon(str(self.base_dir / "Images" / "export_to_csv.png")))
        self.act_export_csv.triggered.connect(self.export_csv)
        file_menu.addAction(self.act_export_csv)

        file_menu.addSeparator()

        self.act_exit_app = QAction(_("&Exit"), self)
        self.act_exit_app.setIcon(QIcon(str(self.base_dir / "Images" / "exit.png")))
        self.act_exit_app.setShortcut(QKeySequence.StandardKey.Quit)
        self.act_exit_app.triggered.connect(self.close)
        file_menu.addAction(self.act_exit_app)

        # Edit Menu
        edit_menu = menubar.addMenu(_("&Edit"))

        self.act_undo = QAction(_("&Undo"), self)
        self.act_undo.setIcon(QIcon(str(self.base_dir / "Images" / "undo.png")))
        self.act_undo.setShortcut(QKeySequence.StandardKey.Undo)
        self.act_undo.setEnabled(self.undo_stack.canUndo())
        self.act_undo.triggered.connect(self.undo_stack.undo)
        self.undo_stack.canUndoChanged.connect(self.act_undo.setEnabled)
        edit_menu.addAction(self.act_undo)

        self.act_redo = QAction(_("&Redo"), self)
        self.act_redo.setIcon(QIcon(str(self.base_dir / "Images" / "redo.png")))
        self.act_redo.setShortcut(QKeySequence.StandardKey.Redo)
        self.act_redo.setEnabled(self.undo_stack.canRedo())
        self.act_redo.triggered.connect(self.undo_stack.redo)
        self.undo_stack.canRedoChanged.connect(self.act_redo.setEnabled)
        edit_menu.addAction(self.act_redo)

        edit_menu.addSeparator()

        self.act_select_all = QAction(_("Select All"), self)
        self.act_select_all.setShortcut(QKeySequence.StandardKey.SelectAll)
        self.act_select_all.triggered.connect(self.table.selectAll)
        edit_menu.addAction(self.act_select_all)

        # Config Menu
        config_menu = menubar.addMenu(_("&Config"))
        self.act_config = QAction(_("Setup Application..."), self)
        self.act_config.setIcon(QIcon(str(self.base_dir / "Images" / "config.png")))
        self.act_config.triggered.connect(self.open_config)
        config_menu.addAction(self.act_config)

        # Help Menu
        help_menu = menubar.addMenu(_("&Help"))

        self.act_help = QAction(_("User Manual"), self)
        self.act_help.setIcon(QIcon(str(self.base_dir / "Images" / "help.png")))
        self.act_help.triggered.connect(self.open_manual)
        help_menu.addAction(self.act_help)

        self.act_about = QAction(_("About StampDatabase"), self)
        self.act_about.setIcon(QIcon(str(self.base_dir / "Images" / "about.png")))
        self.act_about.triggered.connect(self.open_about)
        help_menu.addAction(self.act_about)

    def _init_toolbar(self):
        """Initialize top shortcut ToolBar."""
        toolbar = QToolBar(_("Main Toolbar"))
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        toolbar.addAction(self.act_create_db)
        toolbar.addAction(self.act_save_db)
        toolbar.addSeparator()
        toolbar.addAction(self.act_undo)
        toolbar.addAction(self.act_redo)
        toolbar.addSeparator()
        toolbar.addAction(self.act_import_csv)
        toolbar.addAction(self.act_export_csv)
        toolbar.addSeparator()
        toolbar.addAction(self.act_config)
        toolbar.addAction(self.act_help)
        toolbar.addAction(self.act_about)
        toolbar.addSeparator()
        toolbar.addAction(self.act_exit_app)

    def import_ms_access_to_sqlite(self):
        """Import MS Access database (.mdb / .accdb) and replicate Stamp_List & db_info to a new SQLite database."""
        if not test_ms_access_support():
            self.show_access_warning_popup()
            return

        file_path, _filter = QFileDialog.getOpenFileName(
            self, _("Select MS Access Database"), "", "MS Access Database (*.mdb *.accdb)"
        )
        if not file_path:
            return

        access_path = Path(file_path)
        country_name = access_path.stem

        out_path = self.db_dir / f"{country_name}.db"
        if out_path.exists():
            reply = QMessageBox.question(
                self,
                _("File Exists"),
                _(f"SQLite database '{country_name}.db' already exists. Do you want to overwrite it?"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        try:
            conn_str = f"Driver={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={access_path};"
            access_conn = pyodbc.connect(conn_str)
            access_cur = access_conn.cursor()

            sqlite_conn = sqlite3.connect(out_path)
            sqlite_cur = sqlite_conn.cursor()

            sqlite_cur.execute("""
                CREATE TABLE IF NOT EXISTS Stamp_List (
                    key TEXT PRIMARY KEY,
                    nbr TEXT,
                    year TEXT,
                    type TEXT,
                    valuecolor TEXT,
                    stampDescription1 TEXT,
                    stampDescription TEXT,
                    width TEXT,
                    height TEXT,
                    sequence TEXT,
                    ascii_seq TEXT,
                    sub_nbr TEXT
                )
            """)

            try:
                access_cur.execute(
                    "SELECT key, nbr, year, type, valuecolor, stampDescription1, stampDescription, width, height, sequence, ascii_seq, sub_nbr FROM Stamp_List")
                stamp_rows = access_cur.fetchall()
                for row in stamp_rows:
                    sqlite_cur.execute("""
                        INSERT OR REPLACE INTO Stamp_List (key, nbr, year, type, valuecolor, stampDescription1, stampDescription, width, height, sequence, ascii_seq, sub_nbr)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, tuple(str(val) if val is not None else "" for val in row))
            except Exception as ex:
                QMessageBox.warning(self, _("Table Import Notice"),
                                    f"{_('Could not fully replicate Stamp_List table:')}\n{str(ex)}")

            sqlite_cur.execute("""
                CREATE TABLE IF NOT EXISTS db_info (
                    Author TEXT,
                    Country TEXT,
                    Description TEXT,
                    Version TEXT,
                    Catalogue TEXT,
                    Language TEXT
                )
            """)

            try:
                access_cur.execute("SELECT Author, Country, Description, Version, Catalogue, Language FROM db_info")
                info_rows = access_cur.fetchall()
                for row in info_rows:
                    sqlite_cur.execute("""
                        INSERT INTO db_info (Author, Country, Description, Version, Catalogue, Language)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, tuple(str(val) if val is not None else "" for val in row))
            except Exception:
                sqlite_cur.execute("""
                    INSERT INTO db_info (Author, Country, Description, Version, Catalogue, Language)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, ("Boris du Reau", country_name, f"{country_name} Stamp Catalogue", "1.0", "Yvert", "fr"))

            sqlite_conn.commit()
            access_conn.close()
            sqlite_conn.close()

            self.current_db_type = "sqlite"
            self._load_country_list()
            idx = self.combo_country.findText(country_name)
            if idx != -1:
                self.combo_country.setCurrentIndex(idx)

            QMessageBox.information(
                self,
                _("Import Success"),
                _(f"MS Access database '{country_name}' successfully imported and converted to SQLite!")
            )

        except Exception as e:
            QMessageBox.critical(self, _("Conversion Error"), f"{_('Error importing Access database:')}\n{str(e)}")

    def create_new_sqlite_db(self):
        """Create a new empty SQLite database with Stamp_List and db_info tables."""
        if self.current_db_type != "sqlite":
            QMessageBox.warning(self, _("SQLite Only"), _("Creating a new database is only supported for SQLite."))
            return

        dialog = CreateDatabaseDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            country = data["country"]
            if not country:
                QMessageBox.warning(self, _("Error"), _("Collection name cannot be empty."))
                return

            db_path = self.db_dir / f"{country}.db"
            if db_path.exists():
                QMessageBox.critical(self, _("Error"), _("A database for this country already exists."))
                return

            conn = sqlite3.connect(db_path)
            cur = conn.cursor()

            cur.execute("""
                CREATE TABLE IF NOT EXISTS Stamp_List (
                    key TEXT PRIMARY KEY,
                    nbr TEXT,
                    year TEXT,
                    type TEXT,
                    valuecolor TEXT,
                    stampDescription1 TEXT,
                    stampDescription TEXT,
                    width TEXT,
                    height TEXT,
                    sequence TEXT,
                    ascii_seq TEXT,
                    sub_nbr TEXT
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS db_info (
                    Author TEXT,
                    Country TEXT,
                    Description TEXT,
                    Version TEXT,
                    Catalogue TEXT,
                    Language TEXT
                )
            """)

            cur.execute("""
                INSERT INTO db_info (Author, Country, Description, Version, Catalogue, Language)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (data["author"], country, data["description"], "1.0", data["catalogue"], data["language"]))

            conn.commit()
            conn.close()

            self._load_country_list()
            idx = self.combo_country.findText(country)
            if idx != -1:
                self.combo_country.setCurrentIndex(idx)

            QMessageBox.information(self, _("Success"), _(f"New SQLite database '{country}.db' created successfully."))

    def open_db_info(self):
        """Open database metadata inspector for db_info table."""
        if not self.db_adapter:
            return

        dialog = DatabaseInfoDialog(self.db_adapter, self.current_country, self)
        dialog.exec()

    def _load_country_list(self):
        """Populate country database dropdown."""
        self.combo_country.blockSignals(True)
        self.combo_country.clear()

        self.available_countries = self._detect_available_countries()
        self.combo_country.addItems(self.available_countries)

        self.combo_country.blockSignals(False)

        self.act_create_db.setEnabled(self.current_db_type == "sqlite")

        if self.available_countries:
            self._on_country_changed(0)

    def _on_country_changed(self, index):
        if not self._check_unsaved_changes():
            return

        country_name = self.combo_country.currentText()
        if not country_name:
            return

        if self.current_db_type == "access" and not test_ms_access_support():
            self.show_access_warning_popup()
            self.current_db_type = "sqlite"

        self.current_country = country_name
        if self.db_adapter:
            self.db_adapter.close()

        try:
            self.db_adapter = CountryDatabaseAdapter(country_name, self.db_dir, self.current_db_type)
        except RuntimeError:
            self.show_access_warning_popup()
            self.current_db_type = "sqlite"
            self.db_adapter = CountryDatabaseAdapter(country_name, self.db_dir, "sqlite")

        self.undo_stack.clear()
        self.is_dirty = False

        self.combo_type.blockSignals(True)
        self.combo_type.clear()
        self.combo_type.addItem(_("All"))
        self.combo_type.addItems(self.db_adapter.load_types())
        self.combo_type.blockSignals(False)

        # Charger les types existants dans la liste déroulante de l'éditeur
        self.edit_type.blockSignals(True)
        self.edit_type.clear()
        if self.db_adapter:
            self.edit_type.addItems(self.db_adapter.load_types())
        self.edit_type.blockSignals(False)

        self.combo_year.blockSignals(True)
        self.combo_year.clear()
        self.combo_year.addItem(_("All"))
        self.combo_year.addItems([str(y) for y in self.db_adapter.load_years()])
        self.combo_year.blockSignals(False)

        self._refresh_table()

    def _refresh_table(self):
        if not self.db_adapter:
            return

        self.table.setSortingEnabled(False)

        stamps = self.db_adapter.get_stamps(
            stamp_type=self.combo_type.currentText(),
            year=self.combo_year.currentText(),
            search_nbr=self.edit_search_nbr.text().strip()
        )

        self.table.setRowCount(0)
        for row_idx, stamp in enumerate(stamps):
            key, nbr, year, stype, valcolor, desc1, desc, width, height, seq, ascii_seq, sub_nbr = stamp
            self.table.insertRow(row_idx)

            self.table.setItem(row_idx, 0, QTableWidgetItem(str(nbr or "")))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(year or "")))
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(stype or "")))
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(valcolor or "")))
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(desc1 or "")))
            self.table.setItem(row_idx, 5, QTableWidgetItem(str(desc or "")))

            self.table.item(row_idx, 0).setData(Qt.ItemDataRole.UserRole, stamp)

        self.table.setSortingEnabled(True)

        if self.table.rowCount() > 0:
            self.table.selectRow(0)
            self._on_stamp_selected()

    def _on_stamp_selected(self):
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            return

        row = self.table.currentRow()
        stamp_data = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)

        key, nbr, year, stype, valcolor, desc1, desc, width, height, seq, ascii_seq, sub_nbr = stamp_data

        self.edit_nbr.setText(str(nbr or ""))
        self.edit_sub_nbr.setText(str(sub_nbr or ""))
        self.edit_year.setText(str(year or ""))
        #self.edit_type.setText(str(stype or ""))
        self.edit_type.setCurrentText(str(stype or ""))

        self.edit_valcolor.setText(str(valcolor or ""))
        self.edit_desc1.setPlainText(str(desc1 or ""))
        self.edit_desc.setPlainText(str(desc or ""))
        self.edit_width.setText(str(width or ""))
        self.edit_height.setText(str(height or ""))
        self.edit_sequence.setText(str(seq or ""))
        self.edit_ascii_seq.setText(str(ascii_seq or ""))

        self._load_stamp_image(nbr, stype, sub_nbr)

    def _on_apply_record_edit(self):
        """Push QUndoCommand when user applies modification in editor panel."""
        selected_rows = self.table.selectedItems()
        if not selected_rows or not self.db_adapter:
            return

        row = self.table.currentRow()
        old_stamp_data = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        stamp_key = old_stamp_data[0]

        new_stamp_data = (
            stamp_key,
            self.edit_nbr.text().strip(),
            self.edit_year.text().strip(),
            #self.edit_type.text().strip(),
            self.edit_type.currentText().strip(),
            self.edit_valcolor.text().strip(),
            self.edit_desc1.toPlainText().strip(),
            self.edit_desc.toPlainText().strip(),
            self.edit_width.text().strip(),
            self.edit_height.text().strip(),
            self.edit_sequence.text().strip(),
            self.edit_ascii_seq.text().strip(),
            self.edit_sub_nbr.text().strip()
        )

        cmd = UpdateStampCommand(self, stamp_key, old_stamp_data, new_stamp_data)
        self.undo_stack.push(cmd)

    def _on_add_stamp_record_old(self):
        """Add a new empty stamp record."""
        if not self.db_adapter:
            return

        new_key = str(self.db_adapter.get_max_key() + 1)
        new_stamp_data = (
            new_key,
            "0",
            "2026",
            "Poste",
            "",
            "",
            _("New Stamp Description"),
            "20",
            "25",
            "1000",
            "1000",
            ""
        )

        cmd = AddStampCommand(self, new_stamp_data)
        self.undo_stack.push(cmd)

    def _on_add_stamp_record(self):
        """Add a new empty stamp record and select it."""
        if not self.db_adapter:
            return

        new_key = str(self.db_adapter.get_max_key() + 1)
        new_stamp_data = (
            new_key,
            "0",
            "2026",
            "Poste",
            "",
            "",
            _("New Stamp Description"),
            "20",
            "25",
            "1000",
            "1000",
            ""
        )

        # Réinitialiser temporairement les filtres pour garantir que le nouveau timbre est visible dans le tableau
        self.combo_type.blockSignals(True)
        self.combo_year.blockSignals(True)
        self.edit_search_nbr.blockSignals(True)

        self.combo_type.setCurrentText(_("All"))
        self.combo_year.setCurrentText(_("All"))
        self.edit_search_nbr.clear()

        self.combo_type.blockSignals(False)
        self.combo_year.blockSignals(False)
        self.edit_search_nbr.blockSignals(False)

        # Exécuter la commande d'ajout
        cmd = AddStampCommand(self, new_stamp_data)
        self.undo_stack.push(cmd)

    def _on_delete_stamp_record(self):
        """Delete selected stamp record(s) - Supports single or multi-selection with explicit count prompt."""
        if not self.db_adapter:
            return

        selected_ranges = self.table.selectedRanges()
        if not selected_ranges:
            return

        selected_rows = sorted(list(set(
            row for r in selected_ranges for row in range(r.topRow(), r.bottomRow() + 1)
        )))

        if not selected_rows:
            return

        stamps_to_delete = []
        for row in selected_rows:
            stamp_data = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            if stamp_data:
                stamps_to_delete.append(stamp_data)

        count = len(stamps_to_delete)
        if count == 0:
            return

        if count == 1:
            msg = _("Are you sure you want to delete 1 selected stamp record?")
        else:
            msg = _(f"Are you sure you want to delete {count} selected stamp records?")

        reply = QMessageBox.question(
            self,
            _("Confirm Delete"),
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            cmd = DeleteStampsCommand(self, stamps_to_delete)
            self.undo_stack.push(cmd)

    def apply_stamp_data(self, key, stamp_data):
        """Apply stamp changes to adapter and interface."""
        if not self.db_adapter:
            return

        _, nbr, year, stype, valcolor, desc1, desc, width, height, seq, ascii_seq, sub_nbr = stamp_data
        self.db_adapter.update_stamp(key, nbr, year, stype, valcolor, desc1, desc, width, height, seq, ascii_seq, sub_nbr)

        self._refresh_table()
        # Recharger les types pour inclure un éventuel nouveau type saisi
        current_val = self.edit_type.currentText()
        self.edit_type.blockSignals(True)
        self.edit_type.clear()
        self.edit_type.addItems(self.db_adapter.load_types())
        self.edit_type.setCurrentText(current_val)
        self.edit_type.blockSignals(False)

    def _update_dirty_state(self, is_clean):
        self.is_dirty = not is_clean
        prefix = "*" if self.is_dirty else ""
        self.setWindowTitle(f"{prefix}StampDatabase - {self.current_country}")

    def save_changes(self):
        """Commit changes to database."""
        if self.db_adapter and self.is_dirty:
            self.db_adapter.commit()
            self.undo_stack.setClean()
            QMessageBox.information(self, _("Saved"), _("Database changes saved successfully."))

    def _check_unsaved_changes(self) -> bool:
        """Prompt confirmation if unsaved changes exist."""
        if self.is_dirty:
            reply = QMessageBox.question(
                self,
                _("Unsaved Changes"),
                _("You have unsaved database changes. Do you want to save them now?"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.save_changes()
                return True
            elif reply == QMessageBox.StandardButton.Cancel:
                return False
        return True

    def getPhotoName(self, stampNumber: str, stampType: str, stampSubNbr) -> str:
        """Generate relative photo filename (exact logic from StampAlbum)."""
        subNbr = ""

        if stampSubNbr is not None and str(stampSubNbr).strip() not in ["", "None"]:
            subNbr = "-" + str(stampSubNbr)

        stampNumber_str = str(stampNumber)
        type_prefix = stampNumber_str[0:2]

        if type_prefix == "A ":
            nbr = "T01-030-" + stampNumber_str[2:] + subNbr + ".jpg"
        elif type_prefix == "BF":
            nbr = "T01-080-" + stampNumber_str[3:] + subNbr + ".jpg"
        elif type_prefix == "S ":
            nbr = "T01-170-" + stampNumber_str[2:] + subNbr + ".jpg"
        elif type_prefix == "BC":
            nbr = "T01-000-BC" + stampNumber_str[3:] + subNbr + ".jpg"
        elif type_prefix == "B ":
            nbr = "T01-000-B" + stampNumber_str[2:] + subNbr + ".jpg"
        elif type_prefix == "P ":
            nbr = "T01-000-P" + stampNumber_str[2:] + subNbr + ".jpg"
        elif type_prefix == "PR":
            nbr = "T01-420-" + stampNumber_str[3:] + subNbr + ".jpg"
        elif type_prefix == "FM":
            nbr = "T01-190-" + stampNumber_str[3:] + subNbr + ".jpg"
        elif type_prefix == "TA":
            nbr = "T01-270-" + stampNumber_str[3:] + subNbr + ".jpg"
        elif type_prefix == "CR":
            nbr = "T01-565-" + stampNumber_str[3:] + subNbr + ".jpg"
        elif type_prefix == "GU":
            nbr = "T01-150-" + stampNumber_str[3:] + subNbr + ".jpg"
        elif type_prefix == "AL":
            nbr = "T01-110-" + stampNumber_str[3:] + subNbr + ".jpg"
        elif type_prefix == "JN":
            nbr = "T01-160-" + stampNumber_str[3:] + subNbr + ".jpg"
        elif type_prefix == "PC":
            nbr = "T01-120-" + stampNumber_str[3:] + subNbr + ".jpg"
        elif type_prefix == "CP":
            nbr = "T01-130-" + stampNumber_str[3:] + subNbr + ".jpg"
        elif type_prefix == "FP":
            nbr = "T01-140-" + stampNumber_str[3:] + subNbr + ".jpg"
        elif type_prefix == "CF":
            nbr = "T01-180-CF-" + stampNumber_str[3:] + subNbr + ".jpg"
        elif type_prefix == "CO":
            nbr = "T01-200-" + stampNumber_str[3:] + subNbr + ".jpg"
        elif type_prefix == "TL":
            nbr = "T01-210-" + stampNumber_str[3:] + subNbr + ".jpg"
        elif type_prefix == "MT":
            nbr = "T01-211-" + stampNumber_str[3:] + subNbr + ".jpg"
        elif type_prefix == "TE":
            nbr = "T01-215-" + stampNumber_str[3:] + subNbr + ".jpg"
        elif type_prefix == "GR":
            nbr = "T01-220-" + stampNumber_str[3:] + subNbr + ".jpg"
        elif type_prefix == "PM":
            nbr = "T01-230-" + stampNumber_str[3:] + subNbr + ".jpg"
        elif type_prefix == "F ":
            nbr = "T01-240-" + stampNumber_str[2:] + subNbr + ".jpg"
        elif type_prefix == "F-":
            nbr = "T01-000-F" + stampNumber_str[2:] + subNbr + ".jpg"
        elif type_prefix == "BI":
            nbr = "T01-250-" + stampNumber_str[2:] + subNbr + ".jpg"
        elif type_prefix == "MA":
            nbr = "T01-251-" + stampNumber_str[2:] + subNbr + ".jpg"
        elif type_prefix == "DI":
            nbr = "T01-260-" + stampNumber_str[2:] + subNbr + ".jpg"
        else:
            stampType_str = str(stampType) if stampType else ""
            if stampType_str == "COURS INSTRUCTION":
                nbr = "T01-252-" + stampNumber_str + subNbr + ".jpg"
            elif stampType_str == "Préoblitéré COURS INSTRUCTION":
                nbr = "T01-253-" + stampNumber_str + subNbr + ".jpg"
            elif stampType_str == "RECOUVREMENT COURS INSTRUCTION":
                nbr = "T01-254-" + stampNumber_str + subNbr + ".jpg"
            elif stampType_str.strip() == "TAXES COURS INSTRUCTION":
                nbr = "T01-255-" + stampNumber_str + subNbr + ".jpg"
            elif stampType_str.strip() == "POSTE AERIENNE MILITAIRE":
                nbr = "T01-256-" + stampNumber_str + subNbr + ".jpg"
            else:
                nbr = "T01-000-" + stampNumber_str + subNbr + ".jpg"

        return nbr

    def _load_stamp_image_old(self, stamp_nbr, stamp_type, stamp_sub_nbr=""):
        """Locate and display stamp image."""
        rel_filename = self.getPhotoName(stamp_nbr, stamp_type, stamp_sub_nbr)

        possible_paths = [
            self.base_dir / "Images" / self.current_country / rel_filename,
            self.base_dir / "Photos" / self.current_country / rel_filename,
            self.base_dir / "Images" / rel_filename,
            self.base_dir / "Photos" / rel_filename,
            self.base_dir / rel_filename
        ]

        found_path = next((p for p in possible_paths if p.exists()), None)

        if found_path:
            pixmap = QPixmap(str(found_path))
            if not pixmap.isNull():
                if pixmap.width() > pixmap.height():
                    scaled_pixmap = pixmap.scaledToWidth(200)
                else:
                    scaled_pixmap = pixmap.scaledToHeight(200)

                self.img_label.setPixmap(scaled_pixmap)
                return

        self.img_label.setText(_("No Photo Available"))

    def _find_file_case_insensitive(self, folder_path: Path, filename: str) -> Path:
        """Recherche un fichier dans un dossier en ignorant la casse des caractères."""
        if not folder_path.is_dir():
            return None

        # 1. Test direct (rapide pour Windows ou si la casse correspond exactement sous Linux)
        exact_path = folder_path / filename
        if exact_path.exists():
            return exact_path

        # 2. Recherche insensible à la casse pour Linux
        target_lower = filename.lower()
        for item in folder_path.iterdir():
            if item.is_file() and item.name.lower() == target_lower:
                return item

        return None

    def _load_stamp_image(self, stamp_nbr, stamp_type, stamp_sub_nbr=""):
        """Locate and display stamp image with case-insensitive resolution for Linux."""
        rel_filename = self.getPhotoName(stamp_nbr, stamp_type, stamp_sub_nbr)

        possible_folders = [
            self.base_dir / "Images" / str(self.current_country),
            self.base_dir / "Photos" / str(self.current_country),
            self.base_dir / "Images",
            self.base_dir / "Photos",
            self.base_dir
        ]

        found_path = None
        for folder in possible_folders:
            found_path = self._find_file_case_insensitive(folder, rel_filename)
            if found_path:
                break

        if found_path:
            pixmap = QPixmap(str(found_path))
            if not pixmap.isNull():
                if pixmap.width() > pixmap.height():
                    scaled_pixmap = pixmap.scaledToWidth(200)
                else:
                    scaled_pixmap = pixmap.scaledToHeight(200)

                self.img_label.setPixmap(scaled_pixmap)
                return

        self.img_label.setText(_("No Photo Available"))

    def _select_stamp_by_key_or_nbr(self, target_key: str, target_nbr: str):
        """Recherche le timbre nouvellement créé dans le tableau, le sélectionne et fait défiler la vue dessus."""
        if not self.table or self.table.rowCount() == 0:
            return

        for row in range(self.table.rowCount()):
            item_nbr = self.table.item(row, 0)
            if not item_nbr:
                continue

            # Récupérer les métadonnées complètes stockées sur la cellule
            stamp_data = item_nbr.data(Qt.ItemDataRole.UserRole)
            if stamp_data:
                key = stamp_data[0]
                nbr = stamp_data[1]

                # Vérifier la correspondance par clé ou par numéro
                if str(key) == str(target_key) or str(nbr) == str(target_nbr):
                    self.table.selectRow(row)
                    self.table.scrollToItem(item_nbr, QTableWidget.ScrollHint.EnsureVisible)
                    self._on_stamp_selected()
                    break

    def import_csv(self):
        """Import CSV file and ADD/INSERT all records into the active database."""
        if not self.db_adapter:
            return

        dialog = CsvDelimiterDialog(self, title="Import CSV Delimiter")
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        delimiter = dialog.get_delimiter()

        file_path, _filter = QFileDialog.getOpenFileName(
            self, _("Import CSV File"), "", "CSV Files (*.csv);;All Files (*)"
        )
        if not file_path:
            return

        try:
            added_count = 0
            with open(file_path, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                for row in reader:
                    raw_key = row.get("key")
                    if not raw_key or self.db_adapter.key_exists(raw_key):
                        new_key = str(self.db_adapter.get_max_key() + 1)
                    else:
                        new_key = str(raw_key)

                    stamp_data = (
                        new_key,
                        row.get("nbr", "0"),
                        row.get("year", ""),
                        row.get("type", "Poste"),
                        row.get("valuecolor", ""),
                        row.get("stampDescription1", ""),
                        row.get("stampDescription", ""),
                        row.get("width", "0"),
                        row.get("height", "0"),
                        row.get("sequence", "1000"),
                        row.get("ascii_seq", "1000"),
                        row.get("sub_nbr", "")
                    )

                    self.db_adapter.insert_stamp(stamp_data)
                    added_count += 1

            self.is_dirty = True
            self._refresh_table()
            QMessageBox.information(
                self,
                _("Import Success"),
                _(f"Successfully added {added_count} stamp record(s) from CSV to the database.")
            )
        except Exception as e:
            QMessageBox.critical(self, _("Import Error"), f"{_('Error importing CSV:')}\n{str(e)}")

    def export_csv(self):
        """Export current catalogue to CSV file."""
        if not self.db_adapter:
            return

        dialog = CsvDelimiterDialog(self, title="Export CSV Delimiter")
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        delimiter = dialog.get_delimiter()

        default_filename = f"{self.current_country}_Catalogue.csv"
        file_path, _filter = QFileDialog.getSaveFileName(
            self, _("Export CSV File"), default_filename, "CSV Files (*.csv)"
        )
        if not file_path:
            return

        stamps = self.db_adapter.get_stamps()

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter=delimiter)
                writer.writerow(
                    ["key", "nbr", "year", "type", "valuecolor", "stampDescription1", "stampDescription", "width", "height", "sequence",
                     "ascii_seq", "sub_nbr"])
                for row in stamps:
                    writer.writerow(list(row))

            QMessageBox.information(self, _("Export Success"), _("Catalogue exported to CSV successfully."))
        except Exception as e:
            QMessageBox.critical(self, _("Export Error"), f"{_('Error exporting CSV:')}\n{str(e)}")

    def open_config(self):
        """Open Application Configuration Dialog and update StampDatabase.cfg upon acceptance."""
        dialog = ConfigDialog(self.config_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_settings = dialog.get_selected_config()
            selected_db_type = new_settings["db_type"]
            selected_language = new_settings["language"]

            # Vérification de la disponibilité de MS Access si sélectionné
            if selected_db_type == "access" and not test_ms_access_support():
                self.show_access_warning_popup()
                selected_db_type = "sqlite"

            # Sauvegarde effective dans le fichier StampDatabase.cfg
            self.config_manager.save_config(
                language=selected_language,
                db_type=selected_db_type,
                last_country=self.current_country or ""
            )

            # Recharger la langue en cache
            import SDAppLanguage
            SDAppLanguage.get_language(force_reload=True)

            self.current_db_type = selected_db_type
            self._load_country_list()

            QMessageBox.information(
                self,
                _("Configuration"),
                _("Configuration updated successfully.\nPlease restart the application to apply language changes.")
            )

    def open_manual(self):
        print("open_manual")
        """Open language-specific manual file."""
        #lang = self.config_manager.get_language()
        lang = self.config_manager.language
        print(lang)
        doc_dir = self.base_dir / "Help"
        print(lang)
        if lang == "fr":
            manual_path = doc_dir / "StampDatabase Manuel utilisateur 19-10-2026.pdf"
        else:
            manual_path = doc_dir / "StampDatabase User Manual 19-10-2026.pdf"

        print(manual_path)
        """Open user manual PDF."""
        #manual_path = self.base_dir / "Help" / "StampAlbum Manuel utilisateur 03-11-2024.pdf"
        if manual_path.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(manual_path)))
        else:
            QMessageBox.warning(self, _("Manual Error"), _("User manual file not found."))

    def open_about(self):
        """Display About Dialog."""
        dialog = SDAboutDlg(self)
        dialog.exec()

    def closeEvent(self, event):
        """Handle application close with unsaved changes prompt."""
        if self._check_unsaved_changes():
            if self.db_adapter:
                self.db_adapter.close()
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())