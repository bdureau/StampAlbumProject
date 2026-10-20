# StampCatalogue

[![Python 3.x](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green.svg)](https://riverbankcomputing.com/software/pyqt/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**StampCatalogue** is a modern desktop application designed for philatelists to manage stamp collections, and track missing stamps.

## 📦 Application Included

**StampCatalogue (`StampCatalogue.py`)**: An independent collection and inventory manager to track owned/missing stamps across multiple custom collections and export Excel mancolists.

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
python StampCatalogue.py
```