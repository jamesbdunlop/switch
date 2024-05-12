import os, sys
import logging
from PySide6 import QtWidgets, QtCore
from themes import factory as st_factory

logger = logging.getLogger(__name__)
logger.propagate = False
logging.basicConfig()


def getCurrentPath():
    if not getattr(sys, "frozen", False):
        currentPath = os.path.dirname(__file__).replace("\\", "/")
        return currentPath
    else:
        currentPath = os.path.dirname(sys.executable).replace("\\", "/")
        return currentPath


class ConfigBrowser(QtWidgets.QFileDialog):
    def __init__(self, themeName, themeColor, toSave=False, parent=None):
        super().__init__(parent=parent)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        if toSave:
            self.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        else:
            self.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)

        self.themeName = themeName
        self.themeColor = themeColor
        self.sheet = st_factory.getThemeData(self.themeName, self.themeColor)
        self.setStyleSheet(self.sheet)

        currentPath = getCurrentPath()
        # this frozen has the effect when running without py2exe of drilling all the way to the widgets folder
        if "widgets" in currentPath:
            tokens = currentPath.split("/")[:-1]
            currentPath = os.path.sep.join(tokens)

        configPath = os.path.join(currentPath, "configs")
        self._dir = QtCore.QDir()
        self._dir.setPath(configPath)
        self._dir.makeAbsolute()
        self.setDirectory(self._dir.path())
        self.resize(600, 500)


if __name__ == "__main__":
    qtapp = QtWidgets.QApplication(sys.argv)
    win = ConfigBrowser(themeName="core", themeColor="")
    win.show()
    sys.exit(qtapp.exec())
