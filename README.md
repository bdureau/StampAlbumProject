# Stamp Album Creator

[![Python 3.x](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green.svg)](https://riverbankcomputing.com/software/pyqt/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Stamp Album Creator** is a modern desktop application designed for stamp collectors (philatelists) to easily design, customize, and print high-quality stamp album pages. 

Originally written in VBA (Excel) in the early 2000s, this application has been fully modernized and re-engineered in Python 3 and PyQt6.

![Stamp Album Creator Screenshot](stamp%20album.png)

---

## 🌟 Key Features

* **Catalogue & Database Integration:**
  * Connects to country-specific databases (SQLite or Microsoft Access) containing stamp details (years, catalog numbers, face values, descriptions, and physical dimensions).
  * Auto-selects stamp box sizes based on physical dimensions.
  * Easy conversion tool available for Access to SQLite migration ([accessToSqlite](https://github.com/bdureau/accessToSqlite)).

* **Interactive Page Layout Engine:**
  * WYSIWYG graphical scene editor with customizable grid and scale support.
  * Full alignment tools: Align Left/Right/Top/Bottom, Horizontally/Vertically center on page.
  * Even distribution tools for horizontal and vertical spacing between items.
  * Undo/Redo (`Ctrl+Z` / `Ctrl+Y`) and clipboard management (Copy, Cut, Paste).

* **Page Decorators & Customization:**
  * Multiple decorative page border styles (Classic Triple Frame, Simple Frame, Greek Corner Notches, Philatelic Dentelle).
  * Custom page numbers, running header years, and copyright notices (single-page or batch applied across all pages).
  * Rich-text editing with full character-level styling (fonts, colors, sizes, and paragraph alignments).
  * Free-floating image insertion with interactive handles for resizing.

* **Exporting & Printing:**
  * High-resolution print previews (`QPrintPreviewDialog`).
  * PDF export for individual pages or complete multi-page albums.
  * Native portrait and landscape A4 page support.

* **Multi-Language Support:**
  * Built-in localization (English and French UI).
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