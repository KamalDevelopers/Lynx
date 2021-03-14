import confvar
import argparser

# Needs to be above local imports
# If the stealth flag is set then overwrite conf
args = argparser.parse()
if args.l:
    confvar.locale(args.l)
if args.t:
    confvar.theme(args.t)
if args.s:
    confvar.stealth()
else:
    confvar.stealth(False)
confvar.confb()

import adblock
import extension
import bookmark
from browser import *
import threading
import sys
import os

if args.URL:
    open_url_arg(args.URL)

def runbrowser():
    app = QApplication(sys.argv)
    app.setApplicationName(confvar.BROWSER_WINDOW_TITLE)
    
    translator = QTranslator()
    if not confvar.BROWSER_LOCALE:
        confvar.BROWSER_LOCALE = QLocale.system().name()
    print('Localization loaded:', translator.load(confvar.BROWSER_LOCALE + '.qm', '../localization'), confvar.BROWSER_LOCALE)
    app.installTranslator(translator)
    
    window = MainWindow()
    window.setWindowTitle(confvar.BROWSER_WINDOW_TITLE)
  
    if os.path.isfile("./img/icons/" + confvar.BROWSER_STYLESHEET + "-lynx_logo.ico"):
        app.setWindowIcon(QIcon(os.path.abspath("./img/icons/" + confvar.BROWSER_STYLESHEET + "-lynx_logo.ico")))
    else: 
        app.setWindowIcon(QIcon(os.path.abspath('./img/icons/lynx_logo.ico')))

    app.setStyleSheet(open(BASE_PATH + "themes/" + confvar.BROWSER_STYLESHEET + ".qss").read())
    app.exec_()

if __name__ == "__main__":
    adblock.readBlocker()
    extension.readExtensions() 
    bookmark.readBookmarks()
    runbrowser()
