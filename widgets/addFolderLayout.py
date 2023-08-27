import sys
import logging
from PySide2 import QtWidgets, QtCore
from functools import partial
from widgets.base import BaseWidget as BaseWidget

logger = logging.getLogger(__name__)
logger.propagate = False
logging.basicConfig()


class AddFolderLayout(BaseWidget):
    name = QtCore.Signal(str, name="name")

    def __init__(self, themeName, themeColor, parent=None):
        super(AddFolderLayout, self).__init__(
            themeName=themeName, themeColor=themeColor, parent=parent
        )
        self.setWindowTitle("Add Folder Schema")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.wl = QtWidgets.QVBoxLayout(self)
        self.nameInput = QtWidgets.QLineEdit()
        self.nameInput.setPlaceholderText(
            "Enter the name for this subFolder mapping..."
        )

        self.buttonLayout = QtWidgets.QHBoxLayout()
        acceptButton = QtWidgets.QPushButton("Accept")
        acceptButton.clicked.connect(partial(self._commit))
        acceptButton.clicked.connect(self.close)

        closeButton = QtWidgets.QPushButton("close")
        closeButton.clicked.connect(self.close)

        self.wl.addWidget(self.nameInput)
        self.buttonLayout.addWidget(acceptButton)
        self.buttonLayout.addWidget(closeButton)
        self.wl.addLayout(self.buttonLayout)

        self.resize(500, 100)
        self.setTheme((themeName, themeColor))

    def _commit(self):
        name = str(self.nameInput.text())
        logger.debug("Creating subFolder layout: %s", name)
        # self.name.emit(name.upper())
        self.name.emit(name)


if __name__ == "__main__":
    qtapp = QtWidgets.QApplication(sys.argv)
    win = AddFolderLayout(themeName="core", themeColor="")
    win.show()
    sys.exit(qtapp.exec_())
