import logging
from PySide6 import QtCore
from widgets import createSchema as suiw_createSchema
from widgets.base import BaseDockWidget as BaseDockWidget

logger = logging.getLogger(__name__)
logger.propagate = False
logging.basicConfig()


class ConfigDockWidget(BaseDockWidget):
    themeChanged = QtCore.Signal(list, name="themeChanged")
    commit = QtCore.Signal(list, name="commit")
    closed = QtCore.Signal(bool, name="closed")

    def __init__(self, themeName, themeColor, parent=None):
        """

        Args:
            themeName:
            themeColor:
            parent:
        """
        super().__init__(themeName=themeName, themeColor=themeColor, parent=parent)
        self.setWindowTitle("Create Config:")
        self.setObjectName("ConfigDockWidget")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.w = suiw_createSchema.CreateSchemaWidget(
            themeName=themeName, themeColor=themeColor
        )
        self.setWidget(self.w)
        self.themeChanged.connect(self.w.setTheme)

    def setTheme(self, theme):
        super().setTheme(theme)
        self.themeChanged.emit(theme)
