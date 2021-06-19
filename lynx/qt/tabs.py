from PyQt5.QtWidgets import (
    QTabWidget,
)


class TabWidget(QTabWidget):
    tab_ids = 0

    def addTab(self, widget, label, silent=False):
        tab_id = self.tab_ids
        self.tab_ids += 1

        i = super().addTab(widget, label)
        if not silent:
            super().setCurrentIndex(i)

        widget.setAccessibleName(str(tab_id))
        return tab_id

    def findTab(self, tab):
        for i in range(0, super().count()):
            if super().widget(i).accessibleName() == tab.accessibleName():
                return i
        return -1

    def setTabIconId(self, tab, icon):
        if icon.isNull():
            return
        return super().setTabIcon(self.findTab(tab), icon)

    def setTabTextId(self, tab, title):
        return super().setTabText(self.findTab(tab), title)

    def hideTabs(self):
        if self.tabBar().isHidden():
            if self.tabBar().count() > 1:
                return self.tabBar().show()
        return self.tabBar().hide()
