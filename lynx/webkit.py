import platform as arch
from urllib.parse import urlparse
from subprocess import Popen, PIPE

import utils.adblock
import utils.bookmark
import utils.mime
import scripts
import confvar

from PyQt5.QtNetwork import QNetworkProxy
from PyQt5.QtCore import (
    QUrl,
    QObject,
    Qt,
    pyqtSlot,
    pyqtSignal,
)
from PyQt5.QtWebEngineWidgets import (
    QWebEnginePage,
)
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtWidgets import (
    QApplication,
)


def set_proxy(string_proxy):
    proxy = QNetworkProxy()
    urlinfo = urlparse(string_proxy)

    if urlinfo.scheme == "socks5":
        proxy.setType(QNetworkProxy.Socks5Proxy)

    elif urlinfo.scheme == "http":
        proxy.setType(QNetworkProxy.HttpProxy)

    proxy.setHostName(urlinfo.hostname)
    proxy.setPort(urlinfo.port)

    QNetworkProxy.setApplicationProxy(proxy)


class WebChannel(QObject):
    def __init__(self):
        super().__init__()

    @pyqtSlot(int, result=list)
    def getBookmarkFavicons(self, script_id):
        if "bookmarks" not in scripts.get_database().get(script_id):
            utils.log.dbg("WARNING")(
                "Script id: " +
                str(script_id) + " invalid permissions"
            )
            return

        result = []
        for bookmark in utils.bookmark.get_bookmarks():
            result.append(bookmark[1])
        return result

    @pyqtSlot(int, result=list)
    def getBookmarkTitles(self, script_id):
        if "bookmarks" not in scripts.get_database().get(script_id):
            utils.log.dbg("WARNING")(
                "Script id: " +
                str(script_id) + " invalid permissions"
            )
            return

        result = []
        for bookmark in utils.bookmark.get_bookmarks():
            result.append(bookmark[2])
        return result

    @pyqtSlot(int, result=list)
    def getBookmarkUrls(self, script_id):
        if "bookmarks" not in scripts.get_database().get(script_id):
            utils.log.dbg("WARNING")(
                "Script id: " +
                str(script_id) + " invalid permissions"
            )
            return

        result = []
        for bookmark in utils.bookmark.get_bookmarks():
            result.append(bookmark[0])
        return result

    @pyqtSlot(int, str, result=str)
    def readFile(self, script_id, path):
        if "filesystem" not in scripts.get_database().get(script_id):
            utils.log.dbg("WARNING")(
                "Script id: " +
                str(script_id) + " invalid permissions"
            )
            return

        with open(confvar.BASE_PATH + path) as F:
            return F.read()

    @pyqtSlot(int, str, str)
    def writeFile(self, script_id, path, data):
        if "filesystem" not in scripts.get_database().get(script_id):
            utils.log.dbg("WARNING")(
                "Script id: " +
                str(script_id) + " invalid permissions"
            )
            return

        with open(confvar.BASE_PATH + path, "w") as F:
            F.write(data)

    @pyqtSlot(int, result=str)
    def locale(self, script_id):
        if not confvar.sparse(confvar.BROWSER_LOCALE):
            return "en_US"
        return confvar.BROWSER_LOCALE


class CustomWebEnginePage(QWebEnginePage):
    actionSignal = pyqtSignal(QWebEnginePage.WebAction, QWebEnginePage)
    ignored_action = False

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

    def ignoreAction(self):
        self.ignored_action = True

    def triggerAction(self, action, checked=False):
        self.actionSignal.emit(action, self)
        if self.ignored_action:
            self.ignored_action = False
            return
        return super().triggerAction(action, checked)

    def chooseFiles(self, mode, oldFiles, acceptMimeTypes):
        if arch.system() != "Linux":
            return super().chooseFiles(mode, oldFiles, acceptMimeTypes)

        if mode:
            multiple_files = "--multiple"
        else:
            multiple_files = ""

        if acceptMimeTypes:
            extensions = utils.mime.get_extensions(acceptMimeTypes)
            file_filter = "Accepted Files | " + ' '.join(extensions)
        else:
            file_filter = "All files | *"

        cmdlist = [
            "zenity",
            multiple_files,
            "--file-selection",
            "--file-filter=" +
            file_filter,
            "--filename="
            + confvar.DOWNLOAD_PATH,
            "--title=Select File",
        ]
        process = Popen(cmdlist, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        stdout, stderr = stdout.decode(), stderr.decode()
        path = stdout.strip()
        return [path]

    def javaScriptConsoleMessage(self, level, msg, linenumber, source_id):
        print('%s:%s: %s' % (source_id, linenumber, msg))


class RequestInterceptor(QWebEngineUrlRequestInterceptor):
    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        if utils.adblock.match(url) is not False:
            info.block(True)
        if confvar.BROWSER_HTTPS_ONLY:
            if url[:5] == "http:":
                info.redirect(QUrl(url.replace("http:", "https:")))
