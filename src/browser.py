import os
import sys
import requests

import adblock
from confvar import *
import lynxutils as lxu

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import PyQt5.QtWebEngineWidgets
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtPrintSupport import *
from PyQt5.QtWebEngineCore import *
    
class RequestInterceptor(QWebEngineUrlRequestInterceptor): 
    def interceptRequest(self, info): 
        url = info.requestUrl().toString()
        if adblock.match(url) != False:
            info.block(True)
interceptor = RequestInterceptor()

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        global BROWSER_HOMEPAGE
        
        font = QFont()
        font.setFamily(BROWSER_FONT_FAMILY)
        font.setPointSize(BROWSER_FONT_SIZE)
        self.setFont(font)

        self.tabs = QTabWidget()
        font = QFont(BROWSER_FONT_FAMILY, BROWSER_FONT_SIZE)
        self.tabs.setFont(font)
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.setTabsClosable(True)
        
        # Shortcuts 
        self.shortcut_closetab = QShortcut(QKeySequence("Ctrl+W"), self)
        self.shortcut_addtab = QShortcut(QKeySequence("Ctrl+H"), self)
        self.shortcut_changetab_f = QShortcut(QKeySequence("Ctrl+K"), self)
        self.shortcut_changetab_b = QShortcut(QKeySequence("Ctrl+J"), self)

        self.shortcut_closetab.activated.connect(self.close_current_tab)
        self.shortcut_changetab_f.activated.connect(self.tab_change_forward)
        self.shortcut_changetab_b.activated.connect(self.tab_change_back)
        self.shortcut_addtab.activated.connect(self.add_new_tab)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)

        self.setCentralWidget(self.tabs)
        self.add_new_tab(QUrl(BROWSER_HOMEPAGE), 'Homepage')

        self.show()
        self.setWindowTitle(BROWSER_WINDOW_TITLE)

    def add_new_tab(self, qurl=None, label="Blank"):
        if qurl is None:
            qurl = QUrl(BROWSER_HOMEPAGE)

        qurl = QUrl(lxu.decodeLynxUrl(qurl))
        QWebEngineProfile.defaultProfile().setRequestInterceptor(interceptor)        
        
        browser = QWebEngineView()
        browser.setUrl(QUrl(qurl))
        
        settings = QWebEngineSettings.defaultSettings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, WEBKIT_JAVASCRIPT_ENABLED)
        settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, WEBKIT_FULLSCREEN_ENABLED)
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, WEBKIT_WEBGL_ENABLED)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, WEBKIT_PLUGINS_ENABLED)
        settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        browser.settings = settings
        
        htabbox = QVBoxLayout()
        navtb = QToolBar("Navigation")
        navtb.setMovable(False) 
        navtb.setMaximumHeight(30)

        back_btn = QAction("", self)
        icon = QIcon("img/arrow_left.ico")
        back_btn.setIcon(icon)
        back_btn.setStatusTip("Back to previous page")
        back_btn.setShortcut('Alt+J')
        back_btn.triggered.connect(lambda: browser.back())

        next_btn = QAction("", self)
        icon = QIcon("img/arrow_right.ico")
        next_btn.setIcon(icon)
        next_btn.setStatusTip("Forward to next page")
        next_btn.setShortcut('Alt+K')
        next_btn.triggered.connect(lambda: browser.forward())
        navtb.addAction(back_btn)
        navtb.addAction(next_btn)

        urlbar = QLineEdit()
        urlbar.returnPressed.connect(lambda: self.navigate_to_url(urlbar.text(), browser))
        urlbar.setFixedHeight(23)
        font = QFont("Noto", 9)
        urlbar.setFont(font)
        navtb.addWidget(urlbar)

        reload_btn = QAction("", self)
        icon = QIcon("img/reload.ico")
        reload_btn.setIcon(icon)
        reload_btn.setStatusTip("Reload page")
        reload_btn.triggered.connect(lambda: browser.reload())
        navtb.addAction(reload_btn)

        htabbox.addWidget(navtb)
        htabbox.addWidget(browser)
        htabbox.setContentsMargins(0, 6, 0, 0)
        tabpanel = QWidget()
        tabpanel.setLayout(htabbox)
        i = self.tabs.addTab(tabpanel, label)
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setCurrentIndex(i)
        
        browser.urlChanged.connect(lambda qurl, browser = browser: urlbar.setText(lxu.encodeLynxUrl(qurl)))

        browser.loadFinished.connect(lambda _, i = i, browser = browser:
                                     self.tabs.setTabText(i, browser.page().title()))

    def tab_open_doubleclick(self, i):
        if i == -1:
            self.add_new_tab()

    def close_current_tab(self, i=-1):
        if i == -1:
            i = self.tabs.currentIndex()
        if self.tabs.count() < 2:
            sys.exit()
        self.tabs.removeTab(i)

    def tab_change_forward(self):
        self.tabs.setCurrentIndex(self.tabs.currentIndex()+1)
    
    def tab_change_back(self):
        self.tabs.setCurrentIndex(self.tabs.currentIndex()-1)

    def update_title(self, browser):
        if browser != self.tabs.currentWidget():
            return

        title = self.tabs.currentWidget().page().title()
        self.setWindowTitle(BROWSER_WINDOW_TITLE)
    
    def update_title(self, url, ):
        self.setWindowTitle(BROWSER_WINDOW_TITLE)

    def navigate_home(self):
        self.tabs.currentWidget().setUrl(QUrl(BROWSER_HOMEPAGE))

    def navigate_to_url(self, u, webview):
        formatU = 0
        if "." not in u and u[:6] != "lynx::":
            u = "https://duckduckgo.com/?q=" + u 
        else:
            formatU = 1
        q = QUrl(u)
        if formatU == 1 and q.toString()[:6] != "lynx::":
            q.setScheme("http")
        
        q = QUrl(lxu.decodeLynxUrl(q))
        webview.setUrl(q)
