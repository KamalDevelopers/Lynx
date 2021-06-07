import subprocess
import utils.bookmark
import utils.lynxutils as lxu

from PyQt5.QtWidgets import (
    QPushButton,
    QDesktopWidget,
)


def shortcuts(window, browser, searchbar):
    shorts = []

    zoom_in = QPushButton("", window)
    zoom_in.setShortcut("Ctrl++")
    zoom_in.clicked.connect(lambda: window.zoom(0.1, browser))

    zoom_out = QPushButton("", window)
    zoom_out.setShortcut("Ctrl+0")
    zoom_out.clicked.connect(lambda: window.zoom(-0.1, browser))

    save_page = QPushButton("", window)
    save_page.setShortcut("Ctrl+S")
    save_page.clicked.connect(lambda: window.save_page(browser))

    mute_page = QPushButton("", window)
    mute_page.setShortcut("Ctrl+M")
    mute_page.clicked.connect(lambda: window.mute_page(browser))

    reload_page = QPushButton("", window)
    reload_page.setShortcut("Ctrl+R")
    reload_page.clicked.connect(lambda: browser.reload())

    reopen_tab = QPushButton("", window)
    reopen_tab.setShortcut("Ctrl+Shift+T")
    reopen_tab.clicked.connect(lambda: window.open_last())

    close_tab_group = QPushButton("", window)
    close_tab_group.setShortcut("Alt+W")
    close_tab_group.clicked.connect(lambda: window.close_current_tab(-2))

    close_browser = QPushButton("", window)
    close_browser.setShortcut("Ctrl+Q")
    close_browser.clicked.connect(lambda: window.close())

    mpv_open = QPushButton("", window)
    mpv_open.setShortcut("Alt+M")
    mpv_open.clicked.connect(
        lambda: subprocess.Popen(
            "mpv " + browser.page().url().toString(), shell=True
        )
    )

    open_bookmarks_page = QPushButton("", window)
    open_bookmarks_page.setShortcut("Alt+B")
    open_bookmarks_page.clicked.connect(
        lambda: window.navigate_to_url("lynx:bookmarks", browser)
    )

    max_view = QPushButton("", window)
    max_view.setShortcut("Alt+F")
    size = QDesktopWidget().screenGeometry(-1)
    max_view.clicked.connect(
        lambda: window.setGeometry(0, 0, size.width(), size.height())
    )

    search_text = QPushButton("", window)
    search_text.setShortcut("Ctrl+F")
    search_text.clicked.connect(
        lambda: window.open_searchbar(browser, searchbar)
    )

    bookmark_page = QPushButton("", window)
    bookmark_page.setShortcut("Ctrl+B")
    bookmark_page.clicked.connect(
        lambda: utils.bookmark.addBookmark(
            browser.page().url().toString(), True
        )
    )

    shorts.append(mpv_open)
    shorts.append(zoom_in)
    shorts.append(zoom_out)
    shorts.append(save_page)
    shorts.append(mute_page)
    shorts.append(reload_page)
    shorts.append(reopen_tab)
    shorts.append(open_bookmarks_page)
    shorts.append(max_view)
    shorts.append(search_text)
    shorts.append(bookmark_page)
    shorts.append(close_tab_group)
    shorts.append(close_browser)

    for s in shorts:
        s.setMaximumWidth(0)

    return shorts
