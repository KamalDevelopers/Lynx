import os
import sys
import requests

import proxy
import bookmark
from webkit import *
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

default_url_open = None 
def open_url_arg(url):
    global default_url_open
    default_url_open = url
interceptor = RequestInterceptor()

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        global BROWSER_HOMEPAGE
        self.last_closed_tab = None

        if BROWSER_PROXY:
            proxy.setProxy(BROWSER_PROXY)

        self.settings = QWebEngineSettings.defaultSettings()
        self.settings.setAttribute(QWebEngineSettings.JavascriptEnabled, WEBKIT_JAVASCRIPT_ENABLED)
        self.settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, WEBKIT_FULLSCREEN_ENABLED)
        self.settings.setAttribute(QWebEngineSettings.WebGLEnabled, WEBKIT_WEBGL_ENABLED)
        self.settings.setAttribute(QWebEngineSettings.PluginsEnabled, WEBKIT_PLUGINS_ENABLED)
        self.settings.setAttribute(QWebEngineSettings.ScrollAnimatorEnabled, 1)
        self.settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, WEBKIT_JAVASCRIPT_POPUPS_ENABLED)
        QWebEngineProfile.defaultProfile().setRequestInterceptor(interceptor)
        if BROWSER_STORE_VISITED_LINKS != True:
            QWebEngineProfile.defaultProfile().clearAllVisitedLinks()

        font = QFont()
        font.setFamily(BROWSER_FONT_FAMILY)
        font.setPointSize(BROWSER_FONT_SIZE)
        self.setFont(font)
        
        font = QFont(BROWSER_FONT_FAMILY, BROWSER_FONT_SIZE)
        self.tabs = QTabWidget()
        self.tabs.setIconSize(QSize(13, 13))
        self.tabs.setFont(font)
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabBar().setExpanding(True)
        self.tabs.tabBar().setAutoHide(1)
        
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

        self.setWindowTitle(BROWSER_WINDOW_TITLE)
        self.add_new_tab()
        self.show()

    def add_new_tab(self, qurl=None, label="Blank", silent=0):
        global default_url_open
        if qurl is None and default_url_open is None:
            qurl = QUrl(BROWSER_HOMEPAGE)
        if default_url_open is not None: 
            qurl = QUrl(default_url_open)
            qurl.setScheme("http")
            default_url_open = None
        
        qurl = QUrl(lxu.decodeLynxUrl(qurl))
        browser = QWebEngineView()
        #cwe = CustomWebEnginePage(self)
        #cwe.set_add_new_tab_h(self.add_new_tab)
        #browser.setPage(cwe)
        # The Custom Web Engine Page feature causes deleteLater() to fail

        browser.page().setBackgroundColor(Qt.darkGray) 
        browser.setUrl(QUrl(qurl))

        if BROWSER_AGENT != None: 
            browser.page().profile().setHttpUserAgent(BROWSER_AGENT)
        browser.settings = self.settings

        htabbox = QVBoxLayout()
        navtb = QToolBar(self.tr("Navigation"))
        navtb.setMovable(False) 
        navtb.setMaximumHeight(30)
        navtb.setIconSize(QSize(10, 10))

        # Hidden Buttons - Keyboard Shortcuts
        zoom_in = QPushButton("", self)
        zoom_in.setShortcut("Ctrl++")
        zoom_in.clicked.connect(lambda: self.zoom(0.1, browser))

        zoom_out = QPushButton("", self)
        zoom_out.setShortcut("Ctrl+0")
        zoom_out.clicked.connect(lambda: self.zoom(-0.1, browser))

        save_page = QPushButton("", self)
        save_page.setShortcut("Ctrl+S")
        save_page.clicked.connect(lambda: self.save_page(browser))
        
        mute_page = QPushButton("", self)
        mute_page.setShortcut("Ctrl+M")
        mute_page.clicked.connect(lambda: self.mute_page(browser))
        
        reload_page = QPushButton("", self)
        reload_page.setShortcut("Ctrl+R")
        reload_page.clicked.connect(lambda: browser.reload())
        
        reopen_tab = QPushButton("", self)
        reopen_tab.setShortcut("Ctrl+Shift+T")
        reopen_tab.clicked.connect(lambda: self.open_last())
        
        max_view = QPushButton("", self)
        max_view.setShortcut("Alt+F")
        size = QDesktopWidget().screenGeometry(-1)
        max_view.clicked.connect(lambda: self.resize(size.width(), size.height()))
        
        navtb.addWidget(zoom_in)
        navtb.addWidget(zoom_out)
        navtb.addWidget(save_page)
        navtb.addWidget(mute_page)
        navtb.addWidget(reload_page)
        navtb.addWidget(max_view)
        navtb.addWidget(reopen_tab)

        zoom_in.setMaximumWidth(0)
        zoom_out.setMaximumWidth(0)
        save_page.setMaximumWidth(0)
        mute_page.setMaximumWidth(0)
        reload_page.setMaximumWidth(0)
        max_view.setMaximumWidth(0)
        reopen_tab.setMaximumWidth(0)

        back_btn = QAction(self.tr("Back (Alt+J)"), self)
        icon = QIcon("img/left_arrow.svg")
        back_btn.setIcon(icon)
        back_btn.setStatusTip("Back to previous page")
        back_btn.setShortcut('Alt+J')
        back_btn.triggered.connect(lambda: browser.back())

        next_btn = QAction(self.tr("Forward (Alt+K)"), self)
        icon = QIcon("img/right_arrow.svg")
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
        urlbar.setStyleSheet("QLineEdit { color: #bfbfbf; }")
        urlbar.setFont(font)

        completer = QCompleter(bookmark.getBookmarks())
        urlbar.setCompleter(completer)
        navtb.addWidget(urlbar)
        
        urlbar_focus = QPushButton("", self)
        urlbar_focus.setShortcut("Ctrl+U")
        urlbar_focus.clicked.connect(lambda: urlbar.setFocus())
        navtb.addWidget(urlbar_focus)
        urlbar_focus.setMaximumWidth(0)
 
        add_tab_btn = QAction(self.tr("Add Tab (Ctrl+H)"), self)
        icon = QIcon("img/add_tab.png")
        add_tab_btn.setIcon(icon)
        add_tab_btn.triggered.connect(lambda: self.add_new_tab())
        navtb.addAction(add_tab_btn)

        htabbox.addWidget(navtb)
        htabbox.addWidget(browser)
        htabbox.setContentsMargins(0, 6, 0, 0)
        tabpanel = QWidget()
        tabpanel.setLayout(htabbox)
        i = self.tabs.addTab(tabpanel, label)
        self.tabs.setTabPosition(QTabWidget.North)
        if silent != 1:
            self.tabs.setCurrentIndex(i)

        self.fullscreen = 0
        urlbar.setFocus()
        browser.page().iconChanged.connect(lambda: self.set_tab_icon(i, browser.page()))
        browser.page().fullScreenRequested.connect(lambda request: (request.accept(), self.fullscreen_webview(htabbox, browser)))
        browser.urlChanged.connect(lambda qurl, browser = browser: urlbar.setText(lxu.encodeLynxUrl(qurl)))
        browser.titleChanged.connect(lambda _, i = i, browser = browser: self.tabs.setTabText(i, browser.page().title()))
    
    def fullscreen_webview(self, htabbox, browser):
        if self.fullscreen == 0:
            self.winsize = self.geometry()
            browser.setParent(None)
            browser.showFullScreen()
            self.fullscreen = 1
            self.settings.setAttribute(QWebEngineSettings.ShowScrollBars, 0)
            self.hide()
        else:
            htabbox.addWidget(browser) 
            browser.showNormal()
            self.show()
            self.setGeometry(self.winsize)
            self.settings.setAttribute(QWebEngineSettings.ShowScrollBars, 1)
            self.fullscreen = 0

    def zoom(self, value, browser):
        changezoom = 0
        if value > 0:
            if browser.zoomFactor() < 4.9:
                changezoom = browser.zoomFactor() + value
        if value < 0:
            if browser.zoomFactor() > .39:
                changezoom = browser.zoomFactor() + value
        browser.setZoomFactor(changezoom)
    
    def save_page(self, browser):
        destination = QFileDialog.getSaveFileName(self, self.tr("Save Page"), OS_HOME + "/Downloads/" + browser.page().title() + ".html", "*.html")
        if destination:
            browser.page().save(destination[0], QWebEngineDownloadItem.SingleHtmlSaveFormat)

    def mute_page(self, browser):
        if browser.page().isAudioMuted():
            browser.page().setAudioMuted(0)
        else:
            browser.page().setAudioMuted(1)

    def set_tab_icon(self, i, webpage):
        #if self.tabs.currentIndex() != i:
        #    return
        if webpage.icon():
            self.tabs.setTabIcon(i, webpage.icon())

    def tab_open_doubleclick(self, i):
        if i == -1:
            self.add_new_tab()

    def open_last(self):
        if self.last_closed_tab:
            self.add_new_tab(self.last_closed_tab)

    def close_current_tab(self, i=-1):
        if i == -1:
            i = self.tabs.currentIndex()
        if self.tabs.count() < 2:
            sys.exit()
        self.last_closed_tab = self.tabs.widget(i).findChildren(QWebEngineView)[0].url()
        self.tabs.widget(i).deleteLater()
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
    
    def navigate_home(self):
        self.tabs.currentWidget().setUrl(QUrl(BROWSER_HOMEPAGE))

    def navigate_to_url(self, url, webview):
        if url == "":
            return
        _qurl = QUrl(url)
        if "." not in url and not lxu.checkLynxUrl(_qurl):
            _qurl = QUrl("https://duckduckgo.com/?q=" + url)
        elif "." in url and not lxu.checkLynxUrl(_qurl):
            _qurl.setScheme("http")
        
        _qurl = QUrl(lxu.decodeLynxUrl(_qurl))
        webview.setUrl(_qurl)
