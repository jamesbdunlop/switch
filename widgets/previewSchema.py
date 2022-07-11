import sys
import logging
from PySide2 import QtWidgets, QtCore
from widgets.base import ThemeMixin
from services import configManger as ss_configManager

logger = logging.getLogger(__name__)
logger.propagate = False
logging.basicConfig()


class PreviewTreeWidget(QtWidgets.QTreeWidget, ThemeMixin):
    def __init__(self, themeName="core", themeColor="", config=None, parent=None):
        QtWidgets.QTreeWidget.__init__(self, parent=parent)
        ThemeMixin.__init__(self, themeName=themeName, themeColor=themeColor)
        self.setWindowTitle("Schema Preview....")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.setTheme([themeName, themeColor])
        self.setStyleSheet(self.sheet)

        self.setColumnCount(1)
        self.setHeaderLabels(["PREVIEW"])
        root = QtWidgets.QTreeWidgetItem()
        root.setText(0, config.configRoot())
        self.addTopLevelItem(root)

        for rootName in config.rootsAslist():
            rootTWI = QtWidgets.QTreeWidgetItem()
            rootTWI.setText(0, rootName)
            root.addChild(rootTWI)

        tli = root.child(0)
        testAssetTWI = QtWidgets.QTreeWidgetItem()
        testAssetTWI.setText(0, "TestName")
        tli.addChild(testAssetTWI)

        parsedData = config._parseData(config.baseFolders())
        self.addChildren(testAssetTWI, parsedData)
        self.expandAll()

        self.resize(400, 600)

    def addChildren(self, root, data):
        for k, v in data.items():
            child = QtWidgets.QTreeWidgetItem()
            child.setText(0, k)
            root.addChild(child)
            if v is not None:
                self.addChildren(child, v)


if __name__ == "__main__":
    qtapp = QtWidgets.QApplication(sys.argv)
    filepath = "D:/CODE/Python/jamesd/switch/configs/baseconfig.json"
    data = ss_configManager.loadJson(filepath)
    config = ss_configManager.Config(data=data)
    config.setName("baseconfig")
    config.setConfigPath(filepath)
    win = PreviewTreeWidget(themeName="core", themeColor="", config=config)
    win.show()
    sys.exit(qtapp.exec_())
