import os
import time
import validators
import platform as arch
from urllib.parse import urlparse
from subprocess import Popen, PIPE

import confvar
import extension
import webkit as wk
import utils.log
import utils.bookmark
import utils.lynxutils as lxu

import qt.shortcuts as shortcuts
from qt.grip import SideGrip
from qt.events import EventHandler

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

        self._grip_size = 8
        self.source_code = False
        self.first_opened = False
        self.last_closed_tab = None
        self.tab_indexes = []

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
        self.settings.setAttribute(QWebEngineSettings.ScrollAnimatorEnabled, 1)
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
                confvar.BROWSER_STORAGE
            )

        try:
            font_id = QFontDatabase.addApplicationFont(
                "font/" + confvar.BROWSER_FONT_FAMILY + ".ttf"
            )
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            self.default_font = QFont(font_family)
            self.default_font.setPixelSize(11)
            self.setFont(self.default_font)
            utils.log.dbg("INFO")(
                "Loaded ttf:" + " font/" + confvar.BROWSER_FONT_FAMILY
            )
        except IndexError:
            utils.log.dbg("ERROR")(
                "Could not load ttf:"
                + " font/"
                + confvar.BROWSER_FONT_FAMILY
                + ".ttf"
            )

        self.tabs = QTabWidget()
        self.tabs.setIconSize(QSize(13, 13))
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabBar().setExpanding(True)
        self.tabs.tabBar().setAutoHide(1)

        self.js_btn_enable = QAction(
            self.tr("Disable Javascript") + " " + "(Alt+Ctrl+A)", self
        )
        self.js_btn_enable.setShortcut("Alt+Ctrl+A")
        icon = QIcon("img/js_enabled.png")
        self.js_btn_enable.setIcon(icon)
        self.js_btn_enable.triggered.connect(lambda: self.javascript_toggle())

        self.js_btn_disable = QAction(
            self.tr("Enable Javascript") + " " + "(Alt+Ctrl+S)", self
        )
        self.js_btn_disable.setShortcut("Alt+Ctrl+S")
        icon = QIcon("img/js_disabled.png")
        self.js_btn_disable.setIcon(icon)
        self.js_btn_disable.setVisible(False)
        self.js_btn_disable.triggered.connect(lambda: self.javascript_toggle())

        self.download_btn = QAction(self.tr("Downloads") + " " + "(Alt+D)", self)
        self.download_btn.setShortcut("Alt+D")
        icon = QIcon("img/download-item/download-idle.png")
        self.download_btn.setIcon(icon)
        self.download_btn.triggered.connect(lambda: self.download_pressed())

        # Shortcuts
        self.shortcut_closetab = QShortcut(QKeySequence("Ctrl+W"), self)
        self.shortcut_addtab = QShortcut(QKeySequence("Ctrl+J"), self)
        self.shortcut_changetab_f = QShortcut(QKeySequence("Ctrl+L"), self)
        self.shortcut_changetab_b = QShortcut(QKeySequence("Ctrl+H"), self)
        self.shortcut_store_session = QShortcut(QKeySequence("Alt+X"), self)

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

        browser = QWebEngineView()
        cwe = wk.CustomWebEnginePage(self)
        cwe.actionSignal.connect(self.handle_action)
        cwe.set_add_new_tab_h(self.add_new_tab)
        browser.setPage(cwe)
        browser.page().setBackgroundColor(QColor(webkit_background_color))
        browser.channel = QWebChannel()
        browser.channel.registerObject("backend", webchannel)
        browser.page().setWebChannel(browser.channel)
        browser.setUrl(QUrl(qurl))

        if confvar.BROWSER_AGENT is not None:
            browser.page().profile().setHttpUserAgent(confvar.BROWSER_AGENT)
        browser.settings = self.settings

        htabbox = QVBoxLayout()
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

        for s in shortcuts.shortcuts(self, browser, searchbar):
            navtb.addWidget(s)

        back_btn = QAction(self.tr("Back") + " " + "(Alt+J)", self)
        icon = QIcon("img/remix/arrow-left-s-line.png")
        back_btn.setIcon(icon)
        back_btn.setShortcut("Alt+J")
        back_btn.triggered.connect(lambda: browser.history().back())

        next_btn = QAction(self.tr("Forward") + " " + "(Alt+K)", self)
        icon = QIcon("img/remix/arrow-right-s-line.png")
        next_btn.setIcon(icon)
        next_btn.setShortcut("Alt+K")
        next_btn.triggered.connect(lambda: browser.history().forward())

        icon = QIcon("img/remix/close-line.png")
        exit_btn = QAction(self.tr("Exit Browser") + " " + "(Ctrl+Q)", self)
        exit_btn.setShortcut("Ctrl+Q")
        exit_btn.setIcon(icon)
        exit_btn.triggered.connect(lambda: self.close())

        navtb.addAction(exit_btn)
        navtb.addAction(back_btn)
        navtb.addAction(next_btn)

        secure_icon = QIcon("img/search.png")

        urlbar = QLineEdit()
        urlbar.returnPressed.connect(
            lambda: self.navigate_to_url(urlbar.text(), browser)
        )
        urlbar.setFixedHeight(26)
        urlbar.addAction(secure_icon, QLineEdit.LeadingPosition)

        # completer = QCompleter(bookmark.get_bookmarks())
        # urlbar.setCompleter(completer)
        for _ in range(0, 10):
            navtb.addSeparator()
        navtb.addWidget(urlbar)

        urlbar_focus = QPushButton("", self)
        urlbar_focus.setShortcut("Ctrl+U")
        urlbar_focus.clicked.connect(lambda: urlbar.setFocus())
        urlbar_focus.setMaximumWidth(0)

        for _ in range(0, 20):
            navtb.addSeparator()
        navtb.addWidget(urlbar_focus)

        add_tab_btn = QAction(self.tr("Add Tab") + " " + "(Ctrl+H)", self)
        icon = QIcon("img/remix/add-line.png")
        add_tab_btn.setIcon(icon)
        add_tab_btn.triggered.connect(lambda: self.add_new_tab())
        navtb.addAction(add_tab_btn)
        navtb.addAction(self.download_btn)

        icon = QIcon("img/remix/spy-line.png")
        stealth_btn = QAction(self.tr("Stealth Mode") + " " + "(Alt+S)", self)
        stealth_btn.setShortcut("Alt+S")
        stealth_btn.setIcon(icon)
        stealth_btn.triggered.connect(lambda: self.launch_stealth())

        if not confvar.STEALTH_FLAG:
            navtb.addAction(stealth_btn)

        if confvar.STEALTH_FLAG:
            navtb.addAction(self.js_btn_enable)
            navtb.addAction(self.js_btn_disable)

        navtb.addSeparator()
        htabbox.addWidget(navtb)
        htabbox.addWidget(searchbar)
        htabbox.addWidget(browser)
        htabbox.setContentsMargins(0, 6, 0, 0)

        tabpanel = QWidget()
        tabpanel.setLayout(htabbox)
        i = self.tabs.addTab(tabpanel, label)
        tab_i = len(self.tab_indexes)
        self.tab_indexes.append(i)

        self.tabs.setTabPosition(QTabWidget.North)
        if silent != 1:
            self.tabs.setCurrentIndex(i)

        self.fullscreen = 0
        urlbar.setFocus()

        if qurl and qurl.toString()[:5] != "lynx:":
            urlbar.setText(qurl.toString())
        self.update_urlbar(urlbar, qurl, 0)

        browser.page().fullScreenRequested.connect(
            lambda request: (
                request.accept(),
                self.fullscreen_webview(htabbox, browser),
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
            lambda _, i=i, browser=browser: self.tabs.setTabText(
                self.tab_indexes[tab_i], browser.page().title()
            )
        )
        browser.page().iconChanged.connect(
            lambda: self.set_tab_icon(self.tab_indexes[tab_i], browser.page())
        )
        browser.page().loadProgress.connect(
            lambda p: self.load_progress(
                p, urlbar, browser.page().url().toString()
            )
        )
        browser.page().urlChanged.connect(
            lambda qurl, browser=browser: self.update_urlbar(urlbar, qurl)
        )
        browser.page().profile().downloadRequested.connect(
            self.download_item_requested
        )
        urlbar.textEdited.connect(
            lambda: self.update_index(self.tabs.currentIndex(), tab_i)
        )
        urlbar.textChanged.connect(lambda: self.shorten_url(urlbar))

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

    def view_source(self, page, url):
        page.toHtml(lambda html: self.set_source(html))
        self.view_source_url = "view-source:" + url
        QTimer.singleShot(
            100, lambda: self.navigate_to_url("view-source:" + url, page)
        )

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
        if action == QWebEnginePage.ViewSource:
            current_url = page.url().toString()
            if "file://" not in current_url:
                self.view_source(page, current_url)

    def load_started(self, urlbar, url, browser):
        self.load_start_time = time.time()
        if url[:5] == "file:":
            wk.set_privileges("*")
            return
        wk.set_privileges()

    def load_finished(self, urlbar, browser):
        if browser.page().url().toString() != "lynx:blank":
            utils.log.dbg("DEBUG")(
                "Loaded webpage in "
                + str(round(time.time() - self.load_start_time, 3))
                + " seconds",
            )
            browser.setFocus()

        if not self.first_opened and arch.system() != "Windows":
            self.show()

        self.first_opened = True

        if wk.get_privileges():
            return

        extension.on_page_load(browser)
        # self.update_urlbar(urlbar, browser.page().url())

    def update_urlbar(self, urlbar, qurl, icon_update=True):
        if "file:///" in qurl.toString():
            if "temp-view.html" in qurl.toString():
                urlbar.setText(self.view_source_url)
                return
        url = lxu.encode_lynx_url(qurl)
        urlbar.setText(url)
        icon = None

        if "lynx:" == urlbar.text()[:5]:
            icon = QIcon("img/search.png")
        if urlbar.text() == "lynx:home" or urlbar.text() == "lynx:blank":
            urlbar.setText("")
        if "https://" == urlbar.text()[:8]:
            icon = QIcon("img/secure.png")
        if "http://" == urlbar.text()[:7] and icon_update:
            icon = QIcon("img/unsecure.png")
        if icon is not None:
            urlbar.removeAction(urlbar.actions()[0])
            urlbar.addAction(icon, QLineEdit.LeadingPosition)

    def shorten_url(self, urlbar):
        text = urlbar.text()
        if validators.url(text):
            url = urlparse(text)
            if confvar.BROWSER_SHORT_URL > 0:
                text = text.replace(url.params, "")
            if confvar.BROWSER_SHORT_URL > 1:
                text = text.replace(url.query, "")
        urlbar.setText(text)

    def update_index(self, i, ti):
        self.tab_indexes[ti] = i

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

        icon = QIcon("img/download-item/" + set_picture + ".png")
        self.download_btn.setIcon(icon)
        if not downloading_item:
            QTimer.singleShot(
                1000,
                lambda: self.download_btn.setIcon(
                    QIcon("img/download-item/download-reset.png")
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

    def set_tab_icon(self, i, webpage):
        if webpage.icon():
            self.tabs.setTabIcon(i, webpage.icon())

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

        if url[:12] == "view-source:":
            if not self.source_code:
                return
            with open(confvar.BASE_PATH + "lynx/view-source.html") as f:
                content = f.read()
            with open("./temp/temp-view.html", "w") as f:
                content = content.replace("{source}", self.source_code)
                f.write(content)
            url = "file:///" + os.path.abspath("./temp/temp-view.html")
            url = url.replace("\\", "/")

        qurl = QUrl(url)
        if "." not in url and not lxu.check_lynx_url(qurl):
            qurl = QUrl("https://duckduckgo.com/?q=" + url)
        elif (
            "." in url
            and not lxu.check_lynx_url(qurl)
            and "file:///" not in url
        ):
            qurl.setScheme("http")

        qurl = QUrl(lxu.decode_lynx_url(qurl))
        webview.setUrl(qurl)

    def load_progress(self, progress, urlbar, url):
        global progress_color_loading
        if url[:5] == "file:" or not url or url == "lynx:blank":
            urlbar.setStyleSheet("background-color: ;")
            return
        if progress < 99:
            percent = progress / 100
            urlbar.setStyleSheet(
                "background: qlineargradient(x1:0, y1:0, x2:1, y2:0,"
                + "stop: 0 "
                + progress_color_loading
                + ", stop: "
                + str(percent)
                + " "
                + progress_color_loading
                + ", stop: "
                + str(percent + 0.001)
                + " rgba(0, 0, 0, 0), stop: 1 #00000005)"
            )
        else:
            urlbar.setStyleSheet("background-color: ;")
