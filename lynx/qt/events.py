import platform as arch
import confvar
import utils.lynxutils as lxu

from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QMainWindow,
    QDesktopWidget,
)


class EventHandler:
    def __init__(self, window):
        self.window = window
        self.m_flag = False

    def closeEvent(self, event):
        self.window.qtsettings.setValue("size", self.window.size())
        self.window.qtsettings.setValue("pos", self.window.pos())
        lxu.lynx_quit()
        event.accept()

    def mousePressEvent(self, event):
        self.m_flag = False
        if self.window.isMaximized():
            return
        if event.button() == Qt.LeftButton:
            self.m_flag = True
            self.m_position = event.globalPos()-self.window.pos()
            event.accept()
            self.window.setCursor(QCursor(Qt.OpenHandCursor))

    def mouseDoubleClickEvent(self, event):
        size = QDesktopWidget().screenGeometry(-1)
        width = self.window.size().width()
        height = self.window.size().height()

        if event.button() == Qt.LeftButton:
            if self.window.isMaximized():
                self.window.showNormal()
                return
            if size.width() == width and height == size.height():
                self.window.setGeometry(50, 50, 1280, 720)
                return
            self.window.showMaximized()
        if event.button() == Qt.RightButton:
            self.window.showMinimized()

    def mouseMoveEvent(self, event):
        if self.m_flag:
            self.window.move(event.globalPos()-self.m_position)
        event.accept()

    def mouseReleaseEvent(self, event):
        self.m_flag = False
        self.window.setCursor(QCursor(Qt.ArrowCursor))

    def resizeEvent(self, event):
        size = QDesktopWidget().screenGeometry(-1)
        width = event.size().width()
        height = event.size().height()

        QMainWindow.resizeEvent(self.window, event)
        self.window.update_grips()

        if size.width() == width and height == size.height():
            self.window.round_corners(0)
            return

        if arch.system() == "Windows" and confvar.BROWSER_BORDERLESS:
            self.window.round_corners()

    def register(self):
        self.window.closeEvent = self.closeEvent
        self.window.mousePressEvent = self.mousePressEvent
        self.window.mouseDoubleClickEvent = self.mouseDoubleClickEvent
        self.window.mouseMoveEvent = self.mouseMoveEvent
        self.window.mouseReleaseEvent = self.mouseReleaseEvent
        self.window.resizeEvent = self.resizeEvent
