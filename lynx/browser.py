import os
import time
import platform as arch
from urllib.parse import urlparse
from subprocess import Popen, PIPE

import confvar
import scripts
import resources
import extension
import webkit as wk
import utils.log
import utils.bookmark
import utils.lynxutils as lxu

import qt.shortcuts as shortcuts
from qt.urlbar import UrlBar
from qt.grip import SideGrip
from qt.events import EventHandler
from qt.tabs import TabWidget

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from PyQt5.QtCore import (
    QSettings,
    QPoint,
    QUrl,
    Qt,
    QTimer,
    QSize,
    QRectF,
)
from PyQt5.QtWidgets import (
    QSplitter,
    QWidget,
    QTabWidget,
    QLineEdit,
    QApplication,
    QFileDialog,
    QMainWindow,
    QAction,
    QShortcut,
    QToolBar,
    QVBoxLayout,
    QPushButton,
)
from PyQt5.QtGui import (
    QIcon,
    QKeySequence,
    QColor,
    QFont,
    QFontDatabase,
    QPainterPath,
    QRegion,
)
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import (
    QWebEngineSettings,
    QWebEngineProfile,
    QWebEngineView,
    QWebEnginePage,
    QWebEngineDownloadItem,
)


default_url_open = None
downloading_item = False
download_directory = confvar.DOWNLOAD_PATH

interceptor = wk.RequestInterceptor()
webchannel = wk.WebChannel()

progress_color_loading = confvar.style.value("QLineEdit", "background-color")
webkit_background_color = confvar.style.value("Background", "background-color")


def open_url_arg(url):
    global default_url_open
    default_url_open = url


if hasattr(Qt, "AA_EnableHighDpiScaling"):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

if hasattr(Qt, "AA_UseHighDpiPixmaps"):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.hide()
        self._grip_size = 8
        self.source_code = False
        self.first_opened = False
        self.last_closed_tab = None

        confvar.style.value(
            "QLineEdit", "font-family", confvar.BROWSER_FONT_FAMILY
        )
        self.setStyleSheet(confvar.style.get())

        if confvar.BROWSER_BORDERLESS:
            self.setWindowFlags(Qt.FramelessWindowHint)
            # Activate corner grips
            # self.corner_grips = [QSizeGrip(self) for i in range(2)]
            self.side_grips = [
                SideGrip(self, Qt.LeftEdge),
                SideGrip(self, Qt.TopEdge),
                SideGrip(self, Qt.RightEdge),
                SideGrip(self, Qt.BottomEdge),
            ]
            self.corner_grips = []

        self.event_handler = EventHandler(self)
        self.event_handler.register()

        self.qtsettings = QSettings("KamalDevelopers", "Lynx")
        self.resize(self.qtsettings.value("size", QSize(1280, 720)))
        self.move(self.qtsettings.value("pos", QPoint(50, 50)))

        if confvar.BROWSER_PROXY:
            wk.set_proxy(confvar.BROWSER_PROXY)

        self.settings = QWebEngineSettings.defaultSettings()
        self.settings.setAttribute(
            QWebEngineSettings.JavascriptEnabled,
            confvar.WEBKIT_JAVASCRIPT_ENABLED,
        )
        self.settings.setAttribute(
            QWebEngineSettings.FullScreenSupportEnabled,
            confvar.WEBKIT_FULLSCREEN_ENABLED,
        )
        self.settings.setAttribute(
            QWebEngineSettings.WebGLEnabled, confvar.WEBKIT_WEBGL_ENABLED
        )
        self.settings.setAttribute(
            QWebEngineSettings.PluginsEnabled, confvar.WEBKIT_PLUGINS_ENABLED
        )
        self.settings.setAttribute(
            QWebEngineSettings.ScrollAnimatorEnabled, True
        )
        self.settings.setAttribute(
            QWebEngineSettings.JavascriptCanOpenWindows,
            confvar.WEBKIT_JAVASCRIPT_POPUPS_ENABLED,
        )
        QWebEngineProfile.defaultProfile().setUrlRequestInterceptor(
            interceptor
        )

        if confvar.BROWSER_STORE_VISITED_LINKS is False:
            QWebEngineProfile.defaultProfile().clearAllVisitedLinks()

        if confvar.BROWSER_STORAGE:
            QWebEngineProfile.defaultProfile().setPersistentStoragePath(
                os.path.abspath(confvar.BROWSER_STORAGE)
            )

        try:
            font_id = QFontDatabase.addApplicationFont(
                ":/fonts/" + confvar.BROWSER_FONT_FAMILY + ".ttf"
            )
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            self.default_font = QFont(font_family)
            self.default_font.setPixelSize(11)
            self.setFont(self.default_font)
            utils.log.dbg("INFO")(
                "Loaded ttf:" + " :/fonts/" + confvar.BROWSER_FONT_FAMILY
            )
        except IndexError:
            utils.log.dbg("ERROR")(
                "Could not load resource:"
                + " :/fonts/"
                + confvar.BROWSER_FONT_FAMILY
                + ".ttf"
            )

        self.tabs = TabWidget()
        self.tabs.setIconSize(QSize(13, 13))
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabBar().setExpanding(True)
        self.tabs.tabBar().setAutoHide(1)
        self.tabs.setFont(QFont(confvar.BROWSER_FONT_FAMILY, 8))

        self.js_btn_enable = QAction(
            self.tr("Disable Javascript")
            + " ("
            + shortcuts.shortcut("enable_js")
            + ")",
            self,
        )
        self.js_btn_enable.setShortcut(shortcuts.shortcut("enable_js"))
        icon = QIcon(":/images/js_enabled.png")
        self.js_btn_enable.setIcon(icon)
        self.js_btn_enable.triggered.connect(lambda: self.javascript_toggle())

        self.js_btn_disable = QAction(
            self.tr("Enable Javascript")
            + " ("
            + shortcuts.shortcut("disable_js")
            + ")",
            self,
        )
        self.js_btn_disable.setShortcut(shortcuts.shortcut("disable_js"))
        icon = QIcon(":/images/js_disabled.png")
        self.js_btn_disable.setIcon(icon)
        self.js_btn_disable.setVisible(False)
        self.js_btn_disable.triggered.connect(lambda: self.javascript_toggle())

        self.download_btn = QAction(
            self.tr("Downloads")
            + " ("
            + shortcuts.shortcut("open_downloads")
            + ")",
            self,
        )
        self.download_btn.setShortcut(shortcuts.shortcut("open_downloads"))
        icon = QIcon(":/images/download-idle.png")
        self.download_btn.setIcon(icon)
        self.download_btn.triggered.connect(lambda: self.download_pressed())

        # Shortcuts
        self.shortcut_closetab = QShortcut(
            QKeySequence(shortcuts.shortcut("close_tab")), self
        )
        self.shortcut_addtab = QShortcut(
            QKeySequence(shortcuts.shortcut("add_tab")), self
        )
        self.shortcut_changetab_f = QShortcut(
            QKeySequence(shortcuts.shortcut("goto_tab_right")), self
        )
        self.shortcut_changetab_b = QShortcut(
            QKeySequence(shortcuts.shortcut("goto_tab_left")), self
        )
        self.shortcut_store_session = QShortcut(
            QKeySequence(shortcuts.shortcut("store_session")), self
        )

        self.shortcut_store_session.activated.connect(
            lambda: lxu.store_session(self.current_urls())
        )
        self.shortcut_closetab.activated.connect(self.close_current_tab)
        self.shortcut_changetab_f.activated.connect(self.tab_change_forward)
        self.shortcut_changetab_b.activated.connect(self.tab_change_back)
        self.shortcut_addtab.activated.connect(self.add_new_tab)

        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.setCentralWidget(self.tabs)

        self.setWindowTitle(confvar.BROWSER_WINDOW_TITLE)

        if confvar.BROWSER_OPEN_URLS:
            for page in confvar.BROWSER_OPEN_URLS:
                self.add_new_tab(QUrl(page))
        else:
            self.add_new_tab()

        if arch.system() == "Windows":
            if confvar.BROWSER_BORDERLESS:
                self.round_corners()
        self.show()

    def add_new_tab(self, qurl=None, label="New Tab", silent=0):
        global default_url_open

        if qurl is None and default_url_open is None:
            if not self.first_opened:
                qurl = QUrl(confvar.BROWSER_HOMEPAGE)
            else:
                qurl = QUrl(confvar.BROWSER_NEWTAB)
        if default_url_open is not None:
            qurl = QUrl(default_url_open)
            qurl.setScheme("http")
            default_url_open = None

        qurl = QUrl(lxu.decode_lynx_url(qurl))

        browser = wk.WebEngineView(self)
        cwe = wk.WebEnginePage(self)
        cwe.actionSignal.connect(self.handle_action)
        cwe.set_add_new_tab_h(self.add_new_tab)
        browser.setPage(cwe)

        browser.page().setDefaultBackgroundColor(
            QColor(webkit_background_color)
        )

        browser.channel = QWebChannel()
        browser.channel.registerObject("backend", webchannel)
        browser.page().setWebChannel(browser.channel)
        browser.setUrl(QUrl(qurl))

        if confvar.BROWSER_AGENT is not None:
            browser.page().profile().setHttpUserAgent(confvar.BROWSER_AGENT)

        navtb = QToolBar(self.tr("Navigation"))
        # navtb.addSeparator()
        navtb.setMovable(False)
        navtb.setMaximumHeight(35)
        navtb.setIconSize(QSize(10, 10))

        searchbar = QLineEdit()
        searchbar.returnPressed.connect(
            lambda: self.search_webview(browser, searchbar.text())
        )
        searchbar.setFixedHeight(23)
        searchbar.hide()

        for s in shortcuts.create_shortcuts(self, browser, searchbar):
            navtb.addWidget(s)

        back_btn = QAction(
            self.tr("Back") + " (" + shortcuts.shortcut("history_back") + ")",
            self,
        )
        icon = QIcon(":/images/arrow-left-s-line.png")
        back_btn.setIcon(icon)
        back_btn.setShortcut(shortcuts.shortcut("history_back"))
        back_btn.triggered.connect(lambda: browser.history().back())

        next_btn = QAction(
            self.tr("Forward")
            + " ("
            + shortcuts.shortcut("history_forward")
            + ")",
            self,
        )
        icon = QIcon(":/images/arrow-right-s-line.png")
        next_btn.setIcon(icon)
        next_btn.setShortcut(shortcuts.shortcut("history_forward"))
        next_btn.triggered.connect(lambda: browser.history().forward())

        icon = QIcon(":/images/close-line.png")
        exit_btn = QAction(
            self.tr("Exit Browser")
            + " ("
            + shortcuts.shortcut("exit_browser")
            + ")",
            self,
        )
        exit_btn.setShortcut(shortcuts.shortcut("exit_browser"))
        exit_btn.setIcon(icon)
        exit_btn.triggered.connect(lambda: self.close())

        navtb.addAction(exit_btn)
        navtb.addAction(back_btn)
        navtb.addAction(next_btn)

        urlbar = UrlBar()
        urlbar.setIcon(":/images/search.png")
        urlbar.returnPressed.connect(
            lambda: self.navigate_to_url(urlbar.text(), browser)
        )
        urlbar.setFixedHeight(26)

        # completer = QCompleter(bookmark.get_bookmarks())
        # urlbar.setCompleter(completer)
        for _ in range(0, 10):
            navtb.addSeparator()
        navtb.addWidget(urlbar)

        urlbar_focus = QPushButton("", self)
        urlbar_focus.setShortcut(shortcuts.shortcut("urlbar_focus"))
        urlbar_focus.clicked.connect(lambda: urlbar.setFocus())
        urlbar_focus.setMaximumWidth(0)

        for _ in range(0, 20):
            navtb.addSeparator()
        navtb.addWidget(urlbar_focus)

        add_tab_btn = QAction(
            self.tr("Add Tab") + " (" + shortcuts.shortcut("add_tab") + ")",
            self,
        )
        icon = QIcon(":/images/add-line.png")
        add_tab_btn.setIcon(icon)
        add_tab_btn.triggered.connect(lambda: self.add_new_tab())
        navtb.addAction(add_tab_btn)
        navtb.addAction(self.download_btn)

        icon = QIcon(":/images/spy-line.png")
        stealth_btn = QAction(
            self.tr("Stealth Mode")
            + " ("
            + shortcuts.shortcut("open_stealth")
            + ")",
            self,
        )
        stealth_btn.setShortcut(shortcuts.shortcut("open_stealth"))

        stealth_btn.setIcon(icon)
        stealth_btn.triggered.connect(lambda: self.launch_stealth())

        if not confvar.STEALTH_FLAG:
            navtb.addAction(stealth_btn)

        if confvar.STEALTH_FLAG:
            navtb.addAction(self.js_btn_enable)
            navtb.addAction(self.js_btn_disable)

        inspector = QWebEngineView()
        browser.page().setInspector(inspector)

        view_splitter = QSplitter()
        view_splitter.addWidget(browser)
        view_splitter.addWidget(inspector)
        view_splitter.setCollapsible(1, False)
        view_splitter.setSizes([200, 200, 100])
        view_splitter.setStyleSheet(
            "background-color: " + webkit_background_color + ";"
        )

        navtb.addSeparator()
        htabbox = QVBoxLayout()
        htabbox.addWidget(navtb)
        htabbox.addWidget(searchbar)
        htabbox.addWidget(view_splitter)
        htabbox.setContentsMargins(0, 6, 0, 0)

        tabpanel = QWidget()
        tabpanel.setLayout(htabbox)
        self.tabs.addTab(tabpanel, label, silent)
        self.tabs.setTabPosition(QTabWidget.North)

        self.fullscreen = 0
        urlbar.setFocus()

        if qurl and qurl.toString()[:5] != "lynx:":
            urlbar.setText(qurl.toString())
        urlbar.setUrl(qurl.toString())

        browser.page().fullScreenRequested.connect(
            lambda request: (
                self.fullscreen_webview(request.toggleOn(), htabbox, browser),
                request.accept(),
            )
        )
        browser.page().featurePermissionRequested.connect(
            lambda origin, feature: (
                self.feature_request(origin, feature, browser)
            )
        )
        browser.page().loadFinished.connect(
            lambda: self.load_finished(urlbar, browser)
        )
        browser.page().loadStarted.connect(
            lambda: self.load_started(
                urlbar, browser.page().url().toString(), browser
            )
        )
        browser.page().titleChanged.connect(
            lambda: self.tabs.setTabTextId(tabpanel, browser.page().title())
        )
        browser.page().iconChanged.connect(
            lambda: self.tabs.setTabIconId(tabpanel, browser.page().icon())
        )
        browser.page().loadProgress.connect(
            lambda p: self.load_progress(
                p, urlbar, browser.page().url().toString(), browser
            )
        )
        browser.page().urlChanged.connect(
            lambda qurl: urlbar.setUrl(qurl.toString())
        )
        browser.page().profile().downloadRequested.connect(
            self.download_item_requested
        )

        return browser

    @property
    def grip_size(self):
        return self._grip_size

    def set_grip_size(self, size):
        if size == self._grip_size:
            return
        self._grip_size = max(2, size)
        SideGrip.update(self)

    def update_grips(self):
        SideGrip.update(self)

    def round_corners(self, radius=8):
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), radius, radius)
        mask = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(mask)

    def launch_stealth(self):
        self.close_current_tab(-2)
        self.close_current_tab()
        lxu.launch_stealth(self)

    def set_source(self, html):
        self.source_code = html

    def inspect_page(self, page):
        if not page.inspector:
            utils.log.dbg("WARNING")("No inspector window initialized")
            return
        if not page.devToolsPage():
            page.setDevToolsPage(page.inspector.page())
            page.inspector.show()
            return
        page.setDevToolsPage(None)
        page.inspector.hide()

    def handle_action(self, action, page):
        if action == QWebEnginePage.SavePage:
            self.save_page(page)
            page.ignoreAction()
        if action == QWebEnginePage.OpenLinkInNewTab:
            url = page.contextMenuData().linkUrl()
            self.add_new_tab(url)
        if action == QWebEnginePage.OpenLinkInNewWindow:
            url = page.contextMenuData().linkUrl()
            lxu.launch_lynx(url.toString())
        if action == QWebEnginePage.InspectElement:
            if page.inspector:
                return
            self.inspect_page(page)

    def feature_request(self, origin, feature, browser):
        requested = lxu.feature_parser(feature)

        if (
            not confvar.BROWSER_ALWAYS_ALLOW
            or requested not in confvar.BROWSER_ALWAYS_ALLOW.split(",")
        ):
            browser.page().setFeaturePermission(
                origin, feature, QWebEnginePage.PermissionDeniedByUser
            )
            return

        browser.page().setFeaturePermission(
            origin, feature, QWebEnginePage.PermissionGrantedByUser
        )
        utils.log.dbg("INFO")(
            "Granted " + requested + " permissions to: " + origin.toString()
        )

    def load_started(self, urlbar, url, browser):
        self.load_start_time = time.time()
        extension.on_page_load(browser, True)

        history = browser.page().history()
        last_url = (
            history.itemAt(history.currentItemIndex() - 1).url().toString()
        )

        if not self.first_opened:
            return

        if urlparse(url).hostname in lxu.search_engine_hosts():
            return

        if url[:5] == "file:" or url[:5] == "lynx:" or not last_url:
            browser.hide()
            return

        if urlparse(last_url).hostname != urlparse(url).hostname:
            browser.hide()

    def load_finished(self, urlbar, browser):
        browser.page().runJavaScript(
            """
            navigator.doNotTrack = 1;
            window.doNotTrack = 1;
            navigator.msDoNotTrack = 1;"
            """
        )

        url = browser.page().url().toString()
        browser.page().updateBackgroundColor()
        if url[:12] == "view-source:":
            browser.page().updateBackgroundColor(Qt.white)

        browser.show()
        if url != "lynx:blank":
            utils.log.dbg("DEBUG")(
                "Loaded webpage in "
                + str(round(time.time() - self.load_start_time, 3))
                + " seconds",
            )
            browser.setFocus()

        self.first_opened = True
        urlbar.updateIcon()

        if url[:5] != "file:":
            extension.on_page_load(browser)
            return

        if os.path.isfile(url[7:].replace(".html", ".js")):
            script_id = scripts.get_database().create(
                ["bookmarks", "filesystem", "notifications"]
            )

            with open(url[7:].replace(".html", ".js")) as f:
                js_code = f.read().replace("{id}", script_id)
            browser.page().runJavaScript(js_code, 0)
            return

    def current_urls(self):
        open_urls = []
        for i in range(0, self.tabs.count()):
            open_urls.append(
                self.tabs.widget(i)
                .findChildren(QWebEngineView)[0]
                .url()
                .toString()
            )
        return open_urls

    def fullscreen_webview(self, toggle_on, htabbox, browser):
        if toggle_on:
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

            # Hack to fix the window focus
            self.lower()
            self.raise_()

    def open_searchbar(self, browser, searchbar):
        if searchbar.isHidden():
            searchbar.show()
            searchbar.setFocus()
        else:
            browser.findText("")
            searchbar.setText("")
            searchbar.hide()

    def javascript_toggle(self):
        if self.settings.testAttribute(QWebEngineSettings.JavascriptEnabled):
            self.settings.setAttribute(QWebEngineSettings.JavascriptEnabled, 0)
            self.js_btn_enable.setVisible(False)
            self.js_btn_disable.setVisible(True)
        else:
            self.settings.setAttribute(QWebEngineSettings.JavascriptEnabled, 1)
            self.js_btn_disable.setVisible(False)
            self.js_btn_enable.setVisible(True)

    def search_webview(self, browser, search):
        browser.findText(search)

    def download_item_progress(self, bytes_received, bytes_total):
        global downloading_item
        progress = 100
        if bytes_received > 0 and bytes_total > 0:
            progress = 100 * float(bytes_received) / float(bytes_total)

        images = {
            20: "download-20",
            40: "download-40",
            60: "download-60",
            80: "download-80",
            90: "download-100",
            100: "download-done",
        }
        set_picture = "download-idle"
        for i, val in enumerate(list(images.keys())):
            if progress >= val:
                set_picture = list(images.values())[i]
        if progress >= 100:
            downloading_item = False

        icon = QIcon(":/images/" + set_picture + ".png")
        self.download_btn.setIcon(icon)
        if not downloading_item:
            QTimer.singleShot(
                1000,
                lambda: self.download_btn.setIcon(
                    QIcon(":/images/download-reset.png")
                ),
            )

    def download_pressed(self):
        global download_directory
        lxu.open_folder(download_directory)

    def download_item_requested(self, download):
        global download_directory, downloading_item

        if downloading_item:
            return

        if arch.system() == "Linux":
            cmdlist = [
                "zenity",
                "--file-selection",
                "--save",
                "--confirm-overwrite",
                "--file-filter=All files | *",
                "--filename="
                + confvar.DOWNLOAD_PATH
                + os.path.basename(download.path()),
                "--title=Select File",
            ]
            process = Popen(cmdlist, stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate()
            stdout, stderr = stdout.decode(), stderr.decode()
            path = stdout.strip()
        else:
            path = str(
                QFileDialog.getSaveFileName(
                    self,
                    "Open file",
                    confvar.DOWNLOAD_PATH + os.path.basename(download.path()),
                    "All files | *",
                )[0]
            )

        if not path:
            return

        download.downloadProgress.connect(self.download_item_progress)
        download.setPath(path)
        if download.path() == path:
            download_directory = os.path.dirname(path)
        downloading_item = True
        download.accept()

    def zoom(self, value, browser):
        changezoom = 0
        if value > 0:
            if browser.zoomFactor() < 4.9:
                changezoom = browser.zoomFactor() + value
        if value < 0:
            if browser.zoomFactor() > 0.39:
                changezoom = browser.zoomFactor() + value
        browser.setZoomFactor(changezoom)

    def download_page(self, dest, html):
        with open(dest, "w") as F:
            F.write(html)

    def save_page(self, page):
        if arch.system() == "Linux":
            cmdlist = [
                "zenity",
                "--file-selection",
                "--save",
                "--confirm-overwrite",
                "--file-filter=*.html",
                "--filename=" + confvar.DOWNLOAD_PATH + page.title() + ".html",
                "--title=Select File",
            ]
            process = Popen(cmdlist, stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate()
            stdout, stderr = stdout.decode(), stderr.decode()
            destination = (stdout.strip(), False)
        else:
            destination = QFileDialog.getSaveFileName(
                self,
                self.tr("Save Page"),
                confvar.DOWNLOAD_PATH + page.title() + ".html",
                "*.html",
                options=QFileDialog.DontUseCustomDirectoryIcons,
            )
        if destination[0]:
            page.toHtml(lambda html: self.download_page(destination[0], html))

    def mute_page(self, browser):
        if browser.page().isAudioMuted():
            browser.page().setAudioMuted(0)
        else:
            browser.page().setAudioMuted(1)

    def tab_open_doubleclick(self, i):
        if i == -1:
            self.add_new_tab()

    def open_last(self):
        if self.last_closed_tab:
            self.add_new_tab(self.last_closed_tab)

    def close_current_tab(self, i=-1):
        index = i
        if i == -1 or i == -2:
            index = self.tabs.currentIndex()
        if self.tabs.count() < 2:
            self.close()
        if i == -2:
            for _ in range(0, index):
                self.close_current_tab(0)
            while self.tabs.count() > 1:
                self.close_current_tab(1)
            return

        self.last_closed_tab = (
            self.tabs.widget(index).findChildren(QWebEngineView)[0].url()
        )
        self.tabs.widget(index).findChildren(QWebEngineView)[
            0
        ].page().setParent(None)
        self.tabs.widget(index).deleteLater()
        self.tabs.removeTab(index)

    def tab_change_forward(self):
        self.tabs.setCurrentIndex(self.tabs.currentIndex() + 1)

    def tab_change_back(self):
        self.tabs.setCurrentIndex(self.tabs.currentIndex() - 1)

    def navigate_home(self):
        self.tabs.currentWidget().setUrl(QUrl(confvar.BROWSER_HOMEPAGE))

    def navigate_to_url(self, url, webview):
        if not url:
            return

        qurl = QUrl(url)
        if "." not in url and not lxu.check_lynx_url(qurl):
            qurl = QUrl(confvar.BROWSER_SEARCH_ENGINE.replace("{query}", url))
        elif (
            "." in url
            and not lxu.check_lynx_url(qurl)
            and "file:///" not in url
        ):
            qurl.setScheme("http")

        qurl = QUrl(lxu.decode_lynx_url(qurl))
        webview.setUrl(qurl)

    def load_progress(self, progress, urlbar, url, browser):
        if progress == 100 or not browser.page().history().count():
            urlbar.progress(100, progress_color_loading)
            browser.show()
            return
        urlbar.progress(progress, progress_color_loading)
