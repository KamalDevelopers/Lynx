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
    QTranslator,
    QLocale,
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

    if os.path.isfile(
        "./img/icons/" + confvar.BROWSER_STYLESHEET + "-lynx_logo.ico"
    ):
        app.setWindowIcon(
            QIcon(
                os.path.abspath(
                    "./img/icons/"
                    + confvar.BROWSER_STYLESHEET
                    + "-lynx_logo.ico"
                )
            )
        )
    else:
        app.setWindowIcon(QIcon(os.path.abspath("./img/icons/lynx_logo.ico")))

    confvar.stylesheet_value(
        "QLineEdit", "font-family", confvar.BROWSER_FONT_FAMILY
    )
    # app.setStyleSheet(open(confvar.BASE_PATH + "themes/" + confvar.BROWSER_STYLESHEET + ".qss").read())
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
