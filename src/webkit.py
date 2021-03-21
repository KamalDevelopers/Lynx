import adblock
from confvar import *
import bookmark
import requests
import favicon

from PyQt5.QtCore import QUrl, QObject, Qt, QEvent, pyqtSignal, pyqtSlot, QTranslator, QLocale, QSize
from PyQt5.QtWebEngineWidgets import QWebEngineSettings, QWebEngineProfile, QWebEnginePage
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtWidgets import (QWidget, QApplication, QDialog, QTabWidget, QLineEdit, QMainWindow, QAction,
                             QShortcut, QVBoxLayout, QToolBar, QPushButton, QDesktopWidget, QCompleter)

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
        if not "bookmarks" in privileges:
            print("Insufficient permissions")
            return
        result = []
        for index in range(0, len(bookmark.getBookmarks())):
            favi = favicon.get(bookmark.getBookmarks()[index])[0].url
            result.append(favi)
        return result 

    @pyqtSlot(result=list)
    def getBookmarkTitles(self):
        if not "bookmarks" in privileges:
            print("Insufficient permissions")
            return

        result = []
        hearders = {'headers':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0'}
        for index in range(0, len(bookmark.getBookmarks())):
            n = requests.get(bookmark.getBookmarks()[index], headers=hearders)
            result.append(n.text[n.text.find('<title>') + 7 : n.text.find('</title>')])
        return result

    @pyqtSlot(result=list)
    def getBookmarkUrls(self):
        if not "bookmarks" in privileges:
            print("Insufficient permissions")
            return
        return bookmark.getBookmarks()

    @pyqtSlot(str, result=str)
    def readFile(self, path):
        if not "filesystem" in privileges:
            print("Insufficient permissions")
            return
        with open(BASE_PATH + path) as F:
            return F.read()

    @pyqtSlot(str, str)
    def writeFile(self, path, data):
        if not "filesystem" in privileges:
            print("Insufficient permissions")
            return
        with open(BASE_PATH + path, "w") as F:
            F.write(data)

    @pyqtSlot(result=str)
    def locale(self):
        if not sparse(BROWSER_LOCALE):
            return "en_US"
        return BROWSER_LOCALE

class CustomWebEnginePage(QWebEnginePage):
    # Hook the "add_new_tab" method 
    def set_add_new_tab_h(self, _add_new_tab):
        self.add_new_tab = _add_new_tab

    def acceptNavigationRequest(self, url,  _type, isMainFrame):
        modifiers = QApplication.keyboardModifiers()
        if _type == QWebEnginePage.NavigationTypeLinkClicked and (modifiers & Qt.ControlModifier):
            self.add_new_tab(QUrl(url), silent=1) 
            return False 
        return super().acceptNavigationRequest(url,  _type, isMainFrame)

class RequestInterceptor(QWebEngineUrlRequestInterceptor): 
    def interceptRequest(self, info): 
        url = info.requestUrl().toString()
        if adblock.match(url) != False:
            info.block(True)
        if BROWSER_HTTPS_ONLY:
            if url[:5] == "http:":
                info.redirect(QUrl(url.replace("http:", "https:")))
