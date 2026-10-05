"""
Stamp Album Creator
-------------------
An application designed to create and assemble custom stamp album pages from
database files and image assets.

Originally written in VBA (Excel) in the early 2000s, this application has been
modernized and re-engineered in Python 3 using PyQt6.

Author: Boris du Reau
Year: 2022-2026
"""
import sys
import PyQt6
from PyQt6.QtWidgets import QApplication

from MainWindow import Window


def main():
    """Application entry point."""
    app = QApplication(sys.argv)

    # Set standard Windows widget styling for a consistent desktop layout
    app.setStyle('Windows')

    # Initialize and display the main GUI window
    win = Window()
    win.show()

    # Start the Qt event loop
    sys.exit(app.exec())


if __name__ == '__main__':
    main()