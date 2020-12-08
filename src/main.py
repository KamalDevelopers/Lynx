import confvar
from browser import *
import sys
import os

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName(confvar.BROWSER_WINDOW_TITLE)
    window = MainWindow()
    window.setWindowTitle(confvar.BROWSER_WINDOW_TITLE)
    
    app.setWindowIcon(QIcon('img/lynx_logo.svg'))
    app.setStyleSheet(open(BASE_PATH + "themes/" + BROWSER_STYLESHEET + ".qss").read())
    app.exec_()
