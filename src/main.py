import confvar
import argparser

# Needs to be above local imports
# If the stealth flag is set then overwrite conf
args = argparser.parse()
if args.URL:
    open_url_arg(args.URL)
if args.s:
    confvar.stealth()
else:
    confvar.stealth(False)
confvar.confb()


import adblock
import bookmark
from browser import *

import threading
import sys
import os

def runbrowser():
    app = QApplication(sys.argv)
    app.setApplicationName(confvar.BROWSER_WINDOW_TITLE)
    
    translator = QTranslator()
    if not BROWSER_LOCALE:
        confvar.BROWSER_LOCALE = QLocale.system().name()
    print('Localization loaded:', translator.load(confvar.BROWSER_LOCALE + '.qm', '../localization'), confvar.BROWSER_LOCALE)
    app.installTranslator(translator)
    
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
