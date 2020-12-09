import confvar
import adblock
from browser import *

import threading
import sys
import os

def runbrowser():
    app = QApplication(sys.argv)
    app.setApplicationName(confvar.BROWSER_WINDOW_TITLE)
    window = MainWindow()
    window.setWindowTitle(confvar.BROWSER_WINDOW_TITLE)
    app.setWindowIcon(QIcon('img/lynx_logo.svg'))
    app.setStyleSheet(open(BASE_PATH + "themes/" + BROWSER_STYLESHEET + ".qss").read())
    app.exec_()

if __name__ == "__main__":
    adblock.readBlocker()
    runbrowser()
