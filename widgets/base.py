import os
import logging
from PySide2 import QtWidgets, QtCore, QtGui
from themes import factory as st_factory

logger = logging.getLogger(__name__)
logger.propagate = False
logging.basicConfig()


class IconMixin:
    def _fetchIcon(self, iconName):
        """

        Args:
            iconName (string):
                    name of the icon on disk minus the ext
        Returns:
            QIcon
        """
        self._ICOPATHDIR = QtCore.QDir(st_factory.ICONPATH)
        iconPath = os.path.join(self._ICOPATHDIR.path(), self.themeName, "{}.png".format(iconName))
        iconQDir = QtCore.QDir(iconPath)
        iconQDir.makeAbsolute()
        icon = QtGui.QIcon(iconQDir.absolutePath())
        return icon


class ThemeMixin:
    def __init__(self, themeName, themeColor):
        self.themeName = themeName
        self.themeColor = themeColor
        self.sheet = None

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
        QtWidgets.QWidget.__init__(self, parent=parent)
        ThemeMixin.__init__(self, themeName=themeName, themeColor=themeColor)


class BaseTreeViewWidget(QtWidgets.QTreeView, IconMixin, ThemeMixin):
    def __init__(self, themeName, themeColor, parent=None):
        QtWidgets.QTreeView.__init__(self, parent=parent)
        ThemeMixin.__init__(self, themeName=themeName, themeColor=themeColor)


class BaseDockWidget(QtWidgets.QDockWidget, ThemeMixin):
    def __init__(self, themeName, themeColor, parent=None):
        QtWidgets.QDockWidget.__init__(self, parent=parent)
        ThemeMixin.__init__(self, themeName=themeName, themeColor=themeColor)
