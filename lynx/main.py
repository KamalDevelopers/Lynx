import sys
import os
import time

import confvar
import utils.argparser
import utils.log

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
)
from PyQt5.QtGui import QIcon, QFontDatabase


def runbrowser():
    app = QApplication(sys.argv)
    QFontDatabase.addApplicationFont(
        ":/fonts/" + confvar.BROWSER_FONT_FAMILY + ".ttf"
    )
    app.setApplicationName(confvar.BROWSER_WINDOW_TITLE)
    browser.open_url_arg(utils.argparser.arguments.get().URL)

    translator = QTranslator()
    if not confvar.BROWSER_LOCALE:
        confvar.BROWSER_LOCALE = QLocale.system().name()
    locale_loaded = translator.load(
        confvar.BROWSER_LOCALE + ".qm", "../localization"
    )
    utils.log.dbg("INFO")(
        "Localization loaded: "
        + str(locale_loaded)
        + " "
        + confvar.BROWSER_LOCALE
    )
    app.installTranslator(translator)

    window = browser.MainWindow()
    window.setWindowTitle(confvar.BROWSER_WINDOW_TITLE)

    if os.path.isfile(
        confvar.BASE_PATH
        + "/themes/icons/"
        + confvar.BROWSER_STYLESHEET
        + "-lynx_logo.ico"
    ):
        app.setWindowIcon(
            QIcon(
                os.path.abspath(
                    confvar.BASE_PATH
                    + "/themes/icons/"
                    + confvar.BROWSER_STYLESHEET
                    + "-lynx_logo.ico"
                )
            )
        )
    else:
        app.setWindowIcon(
            QIcon(
                os.path.abspath(
                    confvar.BASE_PATH + "/themes/icons/lynx_logo.ico"
                )
            )
        )

    confvar.style.value(
        "QLineEdit", "font-family", confvar.BROWSER_FONT_FAMILY
    )
    app.setAttribute(Qt.AA_DontShowIconsInMenus, True)
    app.setStyleSheet(confvar.style.get())
    app.exec_()


if __name__ == "__main__":
    start_time = time.time()
    if confvar.BROWSER_ADBLOCKER:
        utils.adblock.read_filter(confvar.BASE_PATH + "adblock/filter.txt")
        utils.log.dbg("DEBUG")(
            "Generated adblock rules: %s seconds"
            % round(time.time() - start_time, 4)
        )

    extension.read_extensions()
    utils.bookmark.read_bookmarks()
    runbrowser()
