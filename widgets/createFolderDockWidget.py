import logging
from PySide2 import QtWidgets, QtCore
from functools import partial
from widgets.base import BaseWidget as BaseWidget
from widgets.base import BaseDockWidget as BaseDockWidget

logger = logging.getLogger(__name__)
logger.propagate = False
logging.basicConfig()


class CreateFolderDockWidget(BaseDockWidget):
    commit = QtCore.Signal(list, name="commit")
    closed = QtCore.Signal(bool, name="closed")

    def __init__(self, themeName, themeColor, config=None, parent=None):
        super(CreateFolderDockWidget, self).__init__(themeName=themeName, themeColor=themeColor, parent=parent)
        self.setWindowTitle("Create Folders:")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.widget = BaseWidget(themeName=themeName, themeColor=themeColor)
        self.mainLayout = QtWidgets.QVBoxLayout(self.widget)

        self.bl = QtWidgets.QHBoxLayout()
        self._assetType = None
        self.config = config

        for assetType in self.config.rootsAslist():
            rb = QtWidgets.QRadioButton(assetType)
            rb.toggled.connect(partial(self._changeAssetType, assetType))
            self.bl.addWidget(rb)

        self.inputName = QtWidgets.QLineEdit()
        self.inputName.setPlaceholderText("... input the name of the asset. Press enter to commit.")
        self.inputName.returnPressed.connect(self._emit)

        self.mainLayout.addLayout(self.bl)
        self.mainLayout.addWidget(self.inputName)
        self.setWidget(self.widget)
        self.widget.resize(100, 400)
        self.resize(100, 400)

        self.mainLayout.addStretch(1)

    def _changeAssetType(self, assetType, _):
        """String from toggling the radioButton

        Args:
            assetType (string):
        """
        logger.debug("assetType changed to: %s", assetType)
        self._assetType = assetType

    def _emit(self):
        """Emit the signal for the list [assetName, assetType]
        """
        self.commit.emit([self.inputName.text(),  self._assetType])

    def closeEvent(self, e) -> None:
        super(CreateFolderDockWidget, self).closeEvent(e)
        self.closed.emit(True)
