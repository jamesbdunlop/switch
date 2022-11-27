import os, sys
import logging
from PySide2 import QtWidgets, QtCore
from themes import factory as st_factory

frozen = getattr(sys, "frozen", "")

logger = logging.getLogger(__name__)
logger.propagate = False
logging.basicConfig()


class ConfigBrowser(QtWidgets.QFileDialog):
    # configSelected = QtCore.Signal(str, name="configSelected")

    def __init__(self, themeName, themeColor, toSave=False, parent=None):
        super(ConfigBrowser, self).__init__(parent=parent)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        if toSave:
            self.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        else:
            self.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)

        self.themeName = themeName
        self.themeColor = themeColor
        self.sheet = st_factory.getThemeData(self.themeName, self.themeColor)
        self.setStyleSheet(self.sheet)

        if not frozen:
            currentPath = os.path.dirname(__file__).replace("\\", "/")
        elif frozen in ("dll", "console_exe", "windows_exe"):
            # py2exe:
            currentPath = os.path.dirname(sys.executable).replace("\\", "/")

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

    # def mouseDoubleClickEvent(self, e):
    #     super(ConfigBrowser, self).mouseDoubleClickEvent(e)
    #     modelIdx = self.indexAt(e.pos())
    #     filePath = self.model().filePath(modelIdx)
    #     if os.path.isfile(filePath) and filePath.endswith(".json"):
    #         print(filePath)
    #
    #     configName = filePath.split("/")[-1].replace(".json", "")
    #     self.configSelected.emit(configName)
    #     self.close()


if __name__ == "__main__":
    qtapp = QtWidgets.QApplication(sys.argv)
    win = ConfigBrowser(themeName="core", themeColor="")
    win.show()
    sys.exit(qtapp.exec_())
