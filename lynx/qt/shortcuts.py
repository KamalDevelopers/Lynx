import subprocess
import confvar
import utils.bookmark
import utils.lynxutils as lxu

from PyQt5.QtWebEngineWidgets import (
    QWebEnginePage,
)
from PyQt5.QtWidgets import (
    QPushButton,
    QDesktopWidget,
)


def shortcut(name):
    return confvar.keyboard_shortcuts[name]


def create_shortcuts(window, browser, searchbar):
    shorts = []

    zoom_in = QPushButton("", window)
    zoom_in.setShortcut(shortcut("zoom_in"))
    zoom_in.clicked.connect(lambda: window.zoom(0.1, browser))

    zoom_out = QPushButton("", window)
    zoom_out.setShortcut(shortcut("zoom_out"))
    zoom_out.clicked.connect(lambda: window.zoom(-0.1, browser))

    save_page = QPushButton("", window)
    save_page.setShortcut(shortcut("save_page"))
    save_page.clicked.connect(lambda: window.save_page(browser.page()))

    mute_page = QPushButton("", window)
    mute_page.setShortcut(shortcut("mute_page"))
    mute_page.clicked.connect(lambda: window.mute_page(browser))

    reload_page = QPushButton("", window)
    reload_page.setShortcut(shortcut("reload_page"))
    reload_page.clicked.connect(lambda: browser.reload())

    inspect_page = QPushButton("", window)
    inspect_page.setShortcut(shortcut("inspect_page"))
    inspect_page.clicked.connect(lambda: window.inspect_page(browser.page()))

    reopen_tab = QPushButton("", window)
    reopen_tab.setShortcut(shortcut("reopen_tab"))
    reopen_tab.clicked.connect(lambda: window.open_last())

    close_tab_group = QPushButton("", window)
    close_tab_group.setShortcut(shortcut("close_tab_group"))
    close_tab_group.clicked.connect(lambda: window.close_current_tab(-2))

    mpv_open = QPushButton("", window)
    mpv_open.setShortcut(shortcut("open_mpv"))
    mpv_open.clicked.connect(
        lambda: subprocess.Popen(
            "mpv " + browser.page().url().toString(), shell=True
        )
    )

    open_bookmarks_page = QPushButton("", window)
    open_bookmarks_page.setShortcut(shortcut("open_bookmarks"))
    open_bookmarks_page.clicked.connect(
        lambda: window.navigate_to_url("lynx:bookmarks", browser)
    )

    max_view = QPushButton("", window)
    max_view.setShortcut(shortcut("max_view"))
    size = QDesktopWidget().screenGeometry(-1)
    max_view.clicked.connect(
        lambda: window.setGeometry(0, 0, size.width(), size.height())
    )

    search_text = QPushButton("", window)
    search_text.setShortcut(shortcut("search_document"))
    search_text.clicked.connect(
        lambda: window.open_searchbar(browser, searchbar)
    )

    bookmark_page = QPushButton("", window)
    bookmark_page.setShortcut(shortcut("bookmark_page"))
    bookmark_page.clicked.connect(
        lambda: utils.bookmark.add_bookmark(
            browser.page().url().toString(),
            browser.page().iconUrl().toString(),
            browser.page().title(),
        )
    )

    shorts.append(mpv_open)
    shorts.append(zoom_in)
    shorts.append(zoom_out)
    shorts.append(save_page)
    shorts.append(mute_page)
    shorts.append(reload_page)
    shorts.append(inspect_page)
    shorts.append(reopen_tab)
    shorts.append(open_bookmarks_page)
    shorts.append(max_view)
    shorts.append(search_text)
    shorts.append(bookmark_page)
    shorts.append(close_tab_group)

    for s in shorts:
        s.setMaximumWidth(0)

    return shorts
