import sys
import os
import time

import confvar
import utils.argparser
import utils.cookies
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
    if confvar.BROWSER_BLOCK_CANVAS:
        sys.argv.append("--disable-reading-from-canvas")
    if confvar.BROWSER_BLOCK_WEBRTC_LEAKS:
        sys.argv.append(
            "--force-webrtc-ip-handling-policy=disable_non_proxied_udp"
        )

    app = QApplication(sys.argv)
    QFontDatabase.addApplicationFont(
        ":/fonts/" + confvar.BROWSER_FONT_FAMILY + ".ttf"
    )
    app.setApplicationName(confvar.BROWSER_WINDOW_TITLE)
    browser.open_url_arg(utils.argparser.arguments.get().URL)

    translator = QTranslator()
    locale_loaded = translator.load(confvar.BROWSER_LOCALE, ":/localization/")
    app.installTranslator(translator)
    if not confvar.BROWSER_LOCALE:
        confvar.BROWSER_LOCALE = QLocale.system().name()
    if confvar.BROWSER_LOCALE != "en_US":
        utils.log.dbg("INFO" if locale_loaded else "ERROR")(
            ["Invalid localization:", "Localization loaded:"][locale_loaded]
            + " :/localization/"
            + confvar.BROWSER_LOCALE
            + ".qm"
        )

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

    app.setAttribute(Qt.AA_DontShowIconsInMenus, True)
    app.exec_()


if __name__ == "__main__":
    start_time = time.time()
    if confvar.BROWSER_ADBLOCKER:
        utils.adblock.read_filter(confvar.BASE_PATH + "adblock/filter.txt")
    if confvar.BROWSER_COOKIE_FILTER:
        utils.cookies.read_filter(confvar.BASE_PATH + "adblock/cookies.txt")

    extension.read_extensions()
    utils.bookmark.read_bookmarks()
    runbrowser()
