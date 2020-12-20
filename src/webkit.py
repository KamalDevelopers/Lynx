import adblock
from confvar import *

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import PyQt5.QtWebEngineWidgets
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtPrintSupport import *
from PyQt5.QtWebEngineCore import *

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

