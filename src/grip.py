from PyQt5 import QtCore, QtGui, QtWidgets
import confvar


def update(window):
    if not confvar.BROWSER_BORDERLESS:
        return
    outRect = window.rect()
    in_rect = outRect.adjusted(
        window.grip_size, window.grip_size,
        -window.grip_size, -window.grip_size
    )

    window.corner_grips[0].setGeometry(
        QtCore.QRect(outRect.topLeft(), in_rect.topLeft()))
    window.corner_grips[1].setGeometry(
        QtCore.QRect(outRect.topRight(), in_rect.topRight()).normalized())

    """
    window.corner_grips[2].setGeometry(
        QtCore.QRect(in_rect.bottomRight(), outRect.bottomRight()))
    window.corner_grips[3].setGeometry(
        QtCore.QRect(outRect.bottomLeft(), in_rect.bottomLeft()).normalized())
    """

    window.side_grips[0].setGeometry(
        0, in_rect.top(), window.grip_size, in_rect.height())
    window.side_grips[1].setGeometry(
        in_rect.left(), 0, in_rect.width(), window.grip_size)
    window.side_grips[2].setGeometry(
        in_rect.left() + in_rect.width(),
        in_rect.top(), window.grip_size, in_rect.height())
    window.side_grips[3].setGeometry(
        window.grip_size, in_rect.top() + in_rect.height(),
        in_rect.width(), window.grip_size)
    [grip.raise_() for grip in window.side_grips + window.corner_grips]


class SideGrip(QtWidgets.QWidget):
    def __init__(self, parent, edge):
        QtWidgets.QWidget.__init__(self, parent)
        if edge == QtCore.Qt.LeftEdge:
            self.setCursor(QtCore.Qt.SizeHorCursor)
            self.resizeFunc = self.resizeLeft
        elif edge == QtCore.Qt.TopEdge:
            self.setCursor(QtCore.Qt.SizeVerCursor)
            self.resizeFunc = self.resizeTop
        elif edge == QtCore.Qt.RightEdge:
            self.setCursor(QtCore.Qt.SizeHorCursor)
            self.resizeFunc = self.resizeRight
        else:
            self.setCursor(QtCore.Qt.SizeVerCursor)
            self.resizeFunc = self.resizeBottom
        self.mousePos = None

    def resizeLeft(self, delta):
        window = self.window()
        width = max(window.minimumWidth(), window.width() - delta.x())
        geo = window.geometry()
        geo.setLeft(geo.right() - width)
        window.setGeometry(geo)

    def resizeTop(self, delta):
        window = self.window()
        height = max(window.minimumHeight(), window.height() - delta.y())
        geo = window.geometry()
        geo.setTop(geo.bottom() - height)
        window.setGeometry(geo)

    def resizeRight(self, delta):
        window = self.window()
        width = max(window.minimumWidth(), window.width() + delta.x())
        window.resize(width, window.height())

    def resizeBottom(self, delta):
        window = self.window()
        height = max(window.minimumHeight(), window.height() + delta.y())
        window.resize(window.width(), height)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.mousePos = event.pos()

    def mouseMoveEvent(self, event):
        if self.mousePos is not None:
            delta = event.pos() - self.mousePos
            self.resizeFunc(delta)

    def mouseReleaseEvent(self, event):
        self.mousePos = None
