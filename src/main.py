import sys
import os
import time

import confvar
import utils.argparser
import utils.log

# Needs to be above local imports
# If the stealth flag is set then overwrite conf
args = utils.argparser.parse()
if args.l:
    confvar.locale(args.l)
if args.t:
    confvar.theme(args.t)
if args.s:
    confvar.stealth()
else:
    confvar.stealth(False)
confvar.confb()
print("Lynx Version", confvar.VERSION)

import utils.bookmark
import utils.adblock
import extension
import browser

from PyQt5.QtWidgets import (
    QApplication,
)
from PyQt5.QtCore import (
    Qt,
    QTranslator,
    QLocale,
    QSize,
)
from PyQt5.QtGui import QIcon, QFontDatabase

if args.URL:
    browser.open_url_arg(args.URL)


def runbrowser():
    app = QApplication(sys.argv)
    QFontDatabase.addApplicationFont(
        "font/" + confvar.BROWSER_FONT_FAMILY + ".ttf"
    )
    app.setApplicationName(confvar.BROWSER_WINDOW_TITLE)

    translator = QTranslator()
    if not confvar.BROWSER_LOCALE:
        confvar.BROWSER_LOCALE = QLocale.system().name()
    locale_loaded = translator.load(
        confvar.BROWSER_LOCALE + ".qm", "../localization"
    )
    utils.log.msg("INFO")(
        "Localization loaded: "
        + str(locale_loaded)
        + " "
        + confvar.BROWSER_LOCALE
    )
    app.installTranslator(translator)

    window = browser.MainWindow()
    window.setWindowTitle(confvar.BROWSER_WINDOW_TITLE)

    app_icon = QIcon()
    app_icon.addFile('img/icons/16x16.ico', QSize(16,16))
    app_icon.addFile('img/icons/24x24.ico', QSize(24,24))
    app_icon.addFile('img/icons/32x32.ico', QSize(32,32))
    app_icon.addFile('img/icons/48x48.ico', QSize(48,48))
    app_icon.addFile('img/icons/256x256.ico', QSize(256,256))
    window.setWindowIcon(app_icon)
    app.setWindowIcon(app_icon)

    confvar.stylesheet_value(
        "QLineEdit", "font-family", confvar.BROWSER_FONT_FAMILY
    )
    # app.setStyleSheet(open(confvar.BASE_PATH + "themes/" + confvar.BROWSER_STYLESHEET + ".qss").read())
    app.setAttribute(Qt.AA_DontShowIconsInMenus, True)
    app.setStyleSheet(confvar.style())
    app.exec_()


if __name__ == "__main__":
    start_time = time.time()
    if confvar.BROWSER_ADBLOCKER:
        utils.adblock.readFilter(confvar.BASE_PATH + "adblock/filter.txt")
        utils.log.msg("DEBUG")(
            "Generated adblock rules: %s seconds"
            % round(time.time() - start_time, 4)
        )

    extension.readExtensions()
    utils.bookmark.readBookmarks()
    runbrowser()
