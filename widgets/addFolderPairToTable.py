import sys
import logging
from PySide2 import QtWidgets, QtCore
from widgets.base import BaseWidget as BaseWidget
from widgets.utils import createLabeledInput

logger = logging.getLogger(__name__)
logger.propagate = False
logging.basicConfig()


class AddFolderPairToTable(BaseWidget):
    folderPair = QtCore.Signal(list, name="folderPair")

    def __init__(self, themeName=None, themeColor=None, parent=None):
        super(AddFolderPairToTable, self).__init__(themeName=themeName, themeColor=themeColor, parent=parent)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        addFolderLayout = QtWidgets.QVBoxLayout(self)
        layout, self.folderName = createLabeledInput("folderName", "Type the name of the folder to create.")
        addFolderLayout.addLayout(layout)

        layout, self.subFolderName = createLabeledInput("subFolderSchemaName", "Type the name of the subfolder schema to create.\nDon't worry if you don't know it now. The default value will be null.")
        self.subFolderName.setText("None")
        addFolderLayout.addLayout(layout)

        buttonLayout = QtWidgets.QHBoxLayout()
        addFolderButton = QtWidgets.QPushButton(self._fetchIcon("iconmonstr-plus-1-240"), "Add")
        addFolderButton.clicked.connect(self._commit)

        closeButton = QtWidgets.QPushButton(self._fetchIcon("iconmonstr-x-mark-4-icon-256"), "Close")
        closeButton.clicked.connect(self.close)

        buttonLayout.addWidget(addFolderButton)
        buttonLayout.addWidget(closeButton)
        addFolderLayout.addLayout(buttonLayout)
        self.resize(600, 200)
        self.setTheme((themeName, themeColor))

    def _commit(self):
        """Emits the folderPair signal.
        """
        self.folderPair.emit([self.folderName.text(), self.subFolderName.text()])
        self.close()


if __name__ == "__main__":
    qtapp = QtWidgets.QApplication(sys.argv)
    win = AddFolderPairToTable(themeName="core", themeColor="")
    win.show()
    sys.exit(qtapp.exec_())
