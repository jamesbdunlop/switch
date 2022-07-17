import logging, sys
from PySide2 import QtWidgets, QtCore
from widgets.base import BaseWidget as BaseWidget
from widgets.base import BaseDockWidget as BaseDockWidget
from themes import factory as t_factory

logger = logging.getLogger(__name__)
logger.propagate = False
logging.basicConfig()


class ThemeEditorDockWidget(BaseDockWidget):
    themeChanged = QtCore.Signal(bool, name="configChanged")

    def __init__(self, themeName, themeColor, parent=None):
        super(ThemeEditorDockWidget, self).__init__(themeName=themeName, themeColor=themeColor, parent=parent)
        self.setWindowTitle("Edit Theme:")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setStyleSheet(self.sheet)
        self.widget = BaseWidget(themeName=themeName, themeColor=themeColor)
        self.mainLayout = QtWidgets.QVBoxLayout(self.widget)

        data = t_factory.fromJSON(self.themeName, self.themeColor)
        self._data = {}
        for entry, value in data.items():
            subLayout = QtWidgets.QHBoxLayout()

            label = QtWidgets.QLabel(entry)

            input = QtWidgets.QLineEdit()
            input.setText(value)

            subLayout.addWidget(label)
            subLayout.addWidget(input)
            self.mainLayout.addLayout(subLayout)
            self._data[entry] = input

        self.saveConfigButton = QtWidgets.QPushButton("Save")
        self.saveConfigButton.clicked.connect(self._saveConfig)

        self.cancelButton = QtWidgets.QPushButton("Close")
        self.cancelButton.clicked.connect(self.close)

        self.mainLayout.addWidget(self.saveConfigButton)
        self.mainLayout.addWidget(self.cancelButton)

        self.setWidget(self.widget)
        self.widget.resize(100, 400)
        self.resize(100, 400)

        self.mainLayout.addStretch(1)

    def _saveConfig(self):
        data = {}
        for k, v in self._data.items():
            data[k] = v.text()

        t_factory.toJSON(data, self.themeName, self.themeColor)
        self.themeChanged.emit(True)


if __name__ == "__main__":
    qtapp = QtWidgets.QApplication(sys.argv)
    win = ThemeEditorDockWidget(themeName="core", themeColor="")
    win.show()
    sys.exit(qtapp.exec_())
