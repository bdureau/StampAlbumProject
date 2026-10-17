# Stamp Album & StampCatalogue Suite

[![Python 3.x](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green.svg)](https://riverbankcomputing.com/software/pyqt/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Stamp Album Suite** is a comprehensive set of modern desktop applications designed for philatelists to design custom album pages, manage stamp collections, and track missing stamps.

Originally created in VBA (Excel) in the early 2000s, the suite has been modernized and re-engineered in Python 3 and PyQt6.

![Stamp Album Creator Screenshot](stamp%20album.png)

---

## 📦 Applications Included

The suite consists of two standalone tools:

1. **Stamp Album Creator (`main.py`)**: A rich graphical editor to layout, format, and print custom stamp album pages.
2. **StampCatalogue (`StampCatalogue.py`)**: An independent collection and inventory manager to track owned/missing stamps across multiple custom collections and export Excel mancolists.

---

## 🌟 Key Features

### 🎨 Stamp Album Creator
* **Catalogue & Database Integration:**
  * Connects to country-specific databases (SQLite or Microsoft Access) containing stamp details (years, catalog numbers, face values, descriptions, and physical dimensions).
  * Auto-selects stamp mount box dimensions based on physical dimensions.
  * Easy conversion tool available for Access to SQLite migration ([accessToSqlite](https://github.com/bdureau/accessToSqlite)).

* **Interactive Page Layout Engine & Precision Tools:**
  * **WYSIWYG Scene Editor:** Custom grid, zoom scaling (25% to 200%), and viewport snapping.
  * **Rulers & Guide Lines:** Interactive millimeter rulers with draggable custom cyan guide lines.
  * **Auto-Arrange Stamps:** Automatic layout algorithm to space out and arrange stamps neatly on the current page.
  * **Alignment & Spacing:** Align Left/Right/Top/Bottom, Horizontally/Vertically center on page, and uniform distribution tools.
  * **Undo/Redo & History:** Full `QUndoStack` support (`Ctrl+Z` / `Ctrl+Y`) with dirty state tracking (visual `*` indicator on unsaved page tabs).
  * **Page Thumbnails Organizer:** Visual thumbnail preview window (`ThumbnailsDlg`) to quickly drag, reorder, or organize album pages.

* **Page Decorators & Customization:**
  * **Page Borders:** Multiple decorative border styles (Classic Triple Frame, Simple Frame, Greek Corner Notches, Philatelic Dentelle) with current page or batch page application.
  * **Page Decorators:** Custom page numbers, running header years, and copyright notices.
  * **Format Support:** Standard A4 and US Letter page sizes in Portrait or Landscape orientations.
  * **Rich Text & Images:** Character-level HTML rich text styling and free-floating image insertion with interactive resize handles.
  * **AlbumEasy Import:** Import script support to load `.txt` layouts from AlbumEasy files.

* **Exporting & Printing:**
  * High-resolution print previews (`QPrintPreviewDialog`).
  * High-quality PDF export for single pages or complete multi-page albums.

---

### 📚 StampCatalogue (Collection & Mancolist Manager)
* **Central Collection Management:**
  * Centralized `collections.db` storing unlimited user-created collections (e.g., *"France Mint 1900-1950"*, *"Monaco Used"*).
  * Opens country databases in **read-only mode** to guarantee catalogue integrity.
* **Filter & Search Module:**
  * Search stamps easily by Country, Type/Category, Year, or Yvert Catalog Number.
* **Detailed Stamp Record & Image Viewer:**
  * Complete stamp details (Face value, color, description).
  * Exact photo resolving engine matching Stamp Album catalogue conventions (`getPhotoName`).
* **Ownership Tracking:**
  * Track status (*Not Owned*, *Owned*, *Manco/Wanted*, *Ordered*), conditions (*MNH \*\**, *MH \**, *Cancelled*, *On Cover*), quantities, purchase prices, and custom notes.
* **Excel Mancolist Generation:**
  * Export styled, auto-formatted `.xlsx` Excel spreadsheets of missing or wanted stamps for any active collection using `openpyxl`.

---

## 🌐 Multi-Language Support

* Fully localized user interfaces in **English** and **French** powered by standard `gettext` catalogs and `AppLanguage`.
* Localized HTML help dialogs.

---

## 🛠️ Installation & Setup

### Prerequisites

Ensure you have Python 3.8 or higher installed on your system.

### Dependencies

Install the required Python packages using `pip`:

```bash
pip install PyQt6 pyodbc
```

> **Note on Databases:**  
> * **SQLite (Recommended):** Requires no additional system installation (uses Python standard library `sqlite3`).  
> * **Microsoft Access (`.mdb` / `.accdb`):** Requires `pyodbc` and Microsoft Access Database Engine Drivers installed on Windows.

---

## 🚀 Usage

### Running the Application

Launch the main application from the command line:

```bash
python main.py
```

### Basic Workflow

1. **New Album Page:** Select page orientation (Portrait or Landscape) and enable default borders.
2. **Add Stamps:** Use `Stamp` -> `New Stamp` to query the database by Country, Type, and Year. Place the generated stamp group onto the page.
3. **Add Titles & Labels:** Use `Objects` -> `New text` or `New Rich Text` to add descriptions, commentary, or section headers.
4. **Align & Layout:** Select multiple items and use the **Align** toolbar to space them evenly or snap them to boundaries.
5. **Export to PDF:** Use `File` -> `Print all pages...` or `Print current to PDF...` to create printable PDF documents.

---

## 📁 Project Structure

```text
├── databases/              # Country catalogue databases (.db or .mdb)
│   ├── master.db           # Global settings, stamp mount sizes, messages
│   └── France.db           # Country stamp catalogue
├── Help/                   # User documentation and localized help files
├── images/                 # GUI icons and application assets
├── locale/                 # Translation catalogs (gettext fr/en)
├── AboutDlg.py             # About dialog component
├── ConfigDlg.py            # Configuration options dialog
├── Databases.py            # Database connector (SQLite / Access)
├── EditStampDlg.py         # Stamp modification dialog
├── GraphicsView.py         # Custom QGraphicsView with clipboard/scaling logic
├── HelpDlg.py              # Localized help viewer
├── main.py                 # Application entry point
├── MainWindow.py           # Main Window container and action management
├── Page.py                 # Core QGraphicsScene page model
├── PageBorder.py           # Decorative border rendering engine
├── ResizablePixmapItem.py  # Image item with resize handles
├── Stamp.py                # Stamp graphic group builder
├── StampDlg.py             # Catalogue stamp selection dialog
├── TextDlg.py              # Standard text editor dialog
├── RichTextDlg.py          # Rich text editor dialog
└── UndoCommands.py         # QUndoStack command implementations
```

---

## 📖 Documentation

For detailed instructions, refer to the full user manual in the repository:
* [Stamp Album User Manual (PDF)](Help/StampAlbum%20Manuel%20utilisateur%2003-11-2024.pdf)

---

## 👤 Author & Credits

* **Author:** Boris du Reau
* **Development History:** 2003–2026 (VBA origins to Python 3 / PyQt6)
* **Access to SQLite Converter:** [bdureau/accessToSqlite](https://github.com/bdureau/accessToSqlite)

---

## 📜 License

This project is licensed under the MIT License — see the `LICENSE` file for details.