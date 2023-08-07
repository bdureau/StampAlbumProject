#
# This an application that will create stamp album pages from a database file and some stamp photos
# This was originally written in VBA in early 2000
# I am re-writing it in Python
# The ability to import and convert old pages generated using Excel will be implemented
# author: Boris du Reau 2022
#
from PyQt6.QtWidgets import (
    QApplication
)

import sys

from MainWindow import Window



# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyle('Windows')

    win = Window()
    win.show()

    #app.exec_()
    app.exec()
