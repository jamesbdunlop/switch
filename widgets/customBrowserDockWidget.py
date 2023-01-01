import logging
from PySide2 import QtCore, QtWidgets
from widgets.base import BaseDockWidget as BaseDockWidget, IconMixin
from widgets import systemFileBrowser as suiw_systemBrowser

logger = logging.getLogger(__name__)
logger.propagate = False
logging.basicConfig()


class CustomBrowserDockWidget(BaseDockWidget, IconMixin):
    closed = QtCore.Signal(str, name="closed")

    def __init__(self, themeName, themeColor, dir, parent=None):
        """

        Args:
            themeName (string):
            themeColor (string):
            parent QtWiget:
        """
        super(CustomBrowserDockWidget, self).__init__(
            themeName=themeName, themeColor=themeColor, parent=parent
        )
        self._dirPath = dir
        self.setWindowTitle(dir)
        self.setObjectName(dir)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        _customBrowserWidget = suiw_systemBrowser.CustomFileBrowser(
            rootDir=dir, themeName=self.themeName, themeColor=self.themeColor
        )
        self.setWidget(_customBrowserWidget)
        self.setWindowIconText(dir)

        tbWidget = QtWidgets.QWidget()
        tbLayout = QtWidgets.QHBoxLayout(tbWidget)
        tbLabelWidget = QtWidgets.QLabel(dir)
        tbclose = QtWidgets.QPushButton(
            self._fetchIcon("iconmonstr-crosshair-1-240"), ""
        )
        tbclose.clicked.connect(self.close)
        tbLayout.addWidget(tbLabelWidget)
        tbLayout.addStretch(1)
        tbLayout.addWidget(tbclose)

        self.setTitleBarWidget(tbWidget)
        self.setTheme((self.themeName, self.themeColor))

    def getDir(self):
        return self._dirPath

    def setTheme(self, theme):
        """

        Args:
            theme (list[themeName, themeColor]):
        """
        super(CustomBrowserDockWidget, self).setTheme(theme)
        self.widget().setTheme(theme)

    def closeEvent(self, event):
        self.closed.emit(self.getDir())
        return super().closeEvent(event)
