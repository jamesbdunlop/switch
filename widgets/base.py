import os, sys
import logging
from PySide6 import QtWidgets, QtCore, QtGui
from themes import factory as st_factory

logger = logging.getLogger(__name__)
logger.propagate = False
logging.basicConfig()


def getIconPath():
    if not getattr(sys, "frozen", False):
        APP_ICONPATH = os.path.dirname(__file__).replace("\\", "/")
        return APP_ICONPATH
    else:
        APP_ICONPATH = "{}".format(os.path.dirname(sys.executable).replace("\\", "/"))
        return APP_ICONPATH


class IconMixin:
    def _fetchIcon(self, iconName):
        """

        Args:
            iconName (string):
                    name of the icon on disk minus the ext
        Returns:
            QIcon
        """
        ICONPATH, _ = st_factory.getPath()
        self._ICOPATHDIR = QtCore.QDir(ICONPATH)
        iconPath = os.path.join(
            self._ICOPATHDIR.path(), self.themeName, "{}.png".format(iconName)
        )
        iconQDir = QtCore.QDir(iconPath)
        iconQDir.makeAbsolute()
        icon = QtGui.QIcon(iconQDir.absolutePath())
        return icon


class ThemeMixin:
    def setTheme(self, theme):
        """

        Args:
            theme (list[themeName, themeColor]):
        """
        themeName, themeColor = theme
        logger.info("themeName: %s", themeName)
        logger.info("themeColor: %s", themeColor)
        self.sheet = st_factory.getThemeData(themeName, themeColor)
        self.themeName = themeName
        self.themeColor = themeColor
        self.setStyleSheet(self.sheet)


class BaseWidget(QtWidgets.QWidget, IconMixin, ThemeMixin):
    def __init__(self, themeName, themeColor, parent=None):
        super().__init__(parent=parent)
        self.setTheme((themeName, themeColor))


class BaseTreeViewWidget(QtWidgets.QTreeView, IconMixin, ThemeMixin):
    def __init__(self, themeName, themeColor, parent=None):
        super().__init__(parent=parent)
        self.setTheme((themeName, themeColor))


class BaseDockWidget(QtWidgets.QDockWidget, ThemeMixin):
    def __init__(self, themeName, themeColor, parent=None):
        super().__init__(parent=parent)
        self.setTheme((themeName, themeColor))

    def setTheme(self, theme):
        super().setTheme(theme=theme)
        if not self.widget() is None:
            self.widget().setStyleSheet(self.sheet)
