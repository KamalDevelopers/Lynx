import confvar
import adblock
import bookmark
from browser import *

import threading
import sys
import os

def runbrowser():
    global BROWSER_LOCALE

    app = QApplication(sys.argv)
    app.setApplicationName(confvar.BROWSER_WINDOW_TITLE)
    
    translator = QTranslator()
    if not BROWSER_LOCALE:
        BROWSER_LOCALE = QLocale.system().name()
    print('Localization loaded:', translator.load(BROWSER_LOCALE + '.qm', '../localization'), BROWSER_LOCALE)
    app.installTranslator(translator)

    if len(sys.argv) > 1: 
        open_url_arg(sys.argv[1])
    window = MainWindow()
    window.setWindowTitle(confvar.BROWSER_WINDOW_TITLE)
  
    if os.path.isfile(confvar.BASE_PATH + "lynx/" + BROWSER_STYLESHEET + "-lynx_logo.png"):
        app.setWindowIcon(QIcon(confvar.BASE_PATH + "lynx/" + BROWSER_STYLESHEET + "-lynx_logo.png")) 
    else: 
        app.setWindowIcon(QIcon('img/lynx_logo.svg'))

    app.setStyleSheet(open(BASE_PATH + "themes/" + BROWSER_STYLESHEET + ".qss").read())
    app.exec_()

if __name__ == "__main__":
    adblock.readBlocker()
    bookmark.readBookmarks()
    runbrowser()
