import logging
from PySide2 import QtCore
from widgets import createSchema as suiw_createSchema
from widgets.base import BaseDockWidget as BaseDockWidget

logger = logging.getLogger(__name__)
logger.propagate = False
logging.basicConfig()


class ConfigDockWidget(BaseDockWidget):
    commit = QtCore.Signal(list, name="commit")
    closed = QtCore.Signal(bool, name="closed")

    def __init__(self, themeName, themeColor, parent=None):
        """

        Args:
            themeName:
            themeColor:
            parent:
        """
        super(ConfigDockWidget, self).__init__(
            themeName=themeName, themeColor=themeColor, parent=parent
        )
        self.setWindowTitle("Create Config:")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.widget = suiw_createSchema.CreateSchemaWidget(
            themeName=themeName, themeColor=themeColor
        )
        self.setWidget(self.widget)

    def setTheme(self, theme):
        """

        Args:
            theme (list[themeName, themeColor]):
        """
        super(ConfigDockWidget, self).setTheme(theme)
        self.widget().setTheme(theme)
