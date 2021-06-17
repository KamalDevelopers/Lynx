from urllib.parse import urlparse
import validators

import utils.lynxutils as lxu
import confvar

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLineEdit


class UrlBar(QLineEdit):
    current_icon = None
    has_focus = False
    raw_url = ""

    def updateIcon(self):
        if (
            self.raw_url[:5] == "lynx:"
            or self.raw_url[:12] == "view-source:"
            or not self.raw_url
        ):
            self.setIcon(":/images/search.png")
        if "https://" == self.raw_url[:8]:
            self.setIcon(":/images/secure.png")
        if "http://" == self.raw_url[:7]:
            self.setIcon(":/images/unsecure.png")

    def setIcon(self, path):
        if self.current_icon == path:
            return False
        if len(super().actions()) > 0:
            super().removeAction(super().actions()[0])
        self.current_icon = path
        super().addAction(QIcon(self.current_icon), QLineEdit.LeadingPosition)

    def setUrl(self, url):
        if url[:5] == "http:" and url[6] != "/":
            url = url[5:]
        encoded_url = lxu.encode_lynx_url(QUrl(url))
        if encoded_url == "lynx:home" or encoded_url == "lynx:blank":
            super().setText("")
            return
        super().setText(encoded_url)
        self.trimUrl()

    def trimUrl(self):
        self.raw_url = super().text()
        text = self.raw_url.replace(" ", "%20")

        if validators.url(text):
            url = urlparse(text)
            if confvar.BROWSER_SHORT_URL == 1:
                text = text.split("&")[0]

            if confvar.BROWSER_SHORT_URL == 2:
                text = text.replace(url.params, "")
                text = text.replace("?" + url.query, "")
                text = text.replace(url.scheme + "://", "")
                if text[:4] == "www.":
                    text = text[4:]

        text = text.replace("%20", " ")
        super().setText(text)

    def progress(self, percent, color):
        if percent < 99:
            decimal = percent / 100
            super().setStyleSheet(
                "background: qlineargradient(x1:0, y1:0, x2:1, y2:0,"
                + "stop: 0 "
                + color
                + ", stop: "
                + str(decimal)
                + " "
                + color
                + ", stop: "
                + str(decimal + 0.001)
                + " rgba(0, 0, 0, 0), stop: 1 #00000005)"
            )
        else:
            super().setStyleSheet("background-color: ;")

    def focusOutEvent(self, event):
        self.has_focus = False
        if super().text() == self.raw_url:
            self.trimUrl()
        return super().focusOutEvent(event)

    def mousePressEvent(self, event):
        if self.has_focus:
            return super().mousePressEvent(event)

        self.has_focus = True
        if self.raw_url and super().text() != self.raw_url:
            super().setText(self.raw_url)
        super().selectAll()
