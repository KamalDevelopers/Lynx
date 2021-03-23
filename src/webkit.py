import utils.adblock
import utils.bookmark
import confvar
import requests
import favicon

from PyQt5.QtCore import (
    QUrl,
    QObject,
    Qt,
    pyqtSlot,
    QThread,
    pyqtSignal,
)
from PyQt5.QtWebEngineWidgets import (
    QWebEnginePage,
)
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtWidgets import (
    QApplication,
)

privileges = []


def setPrivileges(p=[]):
    global privileges
    if p == "*":
        privileges = ["bookmarks", "filesystem"]
        return
    privileges = p


def getPriveleges():
    global privileges
    return privileges


class WebChannel(QObject):
    def __init__(self):
        super().__init__()
        setPrivileges([])

    @pyqtSlot(result=list)
    def getBookmarkFavicons(self):
        if "bookmarks" not in privileges:
            # print("Insufficient permissions")
            return
        result = []
        for index in range(0, len(utils.bookmark.getBookmarks())):
            favi = favicon.get(utils.bookmark.getBookmarks()[index])[0].url
            result.append(favi)
        return result

    @pyqtSlot(result=list)
    def getBookmarkTitles(self):
        if "bookmarks" not in privileges:
            # print("Insufficient permissions")
            return

        result = []
        hearders = {
            "headers": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0"
        }
        for index in range(0, len(utils.bookmark.getBookmarks())):
            n = requests.get(
                utils.bookmark.getBookmarks()[index], headers=hearders
            )
            result.append(
                n.text[n.text.find("<title>") + 7 : n.text.find("</title>")]
            )
        return result

    @pyqtSlot(result=list)
    def getBookmarkUrls(self):
        if "bookmarks" not in privileges:
            # print("Insufficient permissions")
            return
        return utils.bookmark.getBookmarks()

    @pyqtSlot(str, result=str)
    def readFile(self, path):
        if "filesystem" not in privileges:
            # print("Insufficient permissions")
            return
        with open(confvar.BASE_PATH + path) as F:
            return F.read()

    @pyqtSlot(str, str)
    def writeFile(self, path, data):
        if "filesystem" not in privileges:
            # print("Insufficient permissions")
            return
        with open(confvar.BASE_PATH + path, "w") as F:
            F.write(data)

    @pyqtSlot(result=str)
    def locale(self):
        if not confvar.sparse(confvar.BROWSER_LOCALE):
            return "en_US"
        return confvar.BROWSER_LOCALE


class CustomWebEnginePage(QWebEnginePage):
    # Hook the "add_new_tab" method
    def set_add_new_tab_h(self, _add_new_tab):
        self.add_new_tab = _add_new_tab

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        modifiers = QApplication.keyboardModifiers()
        if _type == QWebEnginePage.NavigationTypeLinkClicked and (
            modifiers & Qt.ControlModifier
        ):
            self.add_new_tab(QUrl(url), silent=1)
            return False
        return super().acceptNavigationRequest(url, _type, isMainFrame)

    def javaScriptConsoleMessage(self, level, msg, line, sourceID):
        pass


class RequestInterceptor(QWebEngineUrlRequestInterceptor):
    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        if utils.adblock.match(url) is not False:
            info.block(True)
        if confvar.BROWSER_HTTPS_ONLY:
            if url[:5] == "http:":
                info.redirect(QUrl(url.replace("http:", "https:")))


class MouseEvents(QThread):
    mouse_state_changed = pyqtSignal(int)

    def __init__(self, application, mouse):
        QThread.__init__(self)
        self.mouse_buttons = mouse
        self.app = application
        self.last_state = 0

    def __del__(self):
        self.wait()

    def check(self):
        mouse_state = self.mouse_buttons()
        if mouse_state != self.last_state:
            if mouse_state == Qt.BackButton:
                self.mouse_state_changed.emit(4)
            if mouse_state == Qt.ForwardButton:
                self.mouse_state_changed.emit(5)
            self.last_state = mouse_state

    def run(self):
        while 1:
            self.check()
