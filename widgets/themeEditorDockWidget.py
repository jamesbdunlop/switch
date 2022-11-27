import logging, sys
from functools import partial
from PySide2 import QtWidgets, QtCore, QtGui
from widgets.base import BaseWidget as BaseWidget
from widgets.base import BaseDockWidget as BaseDockWidget
from themes import factory as t_factory

logger = logging.getLogger(__name__)
logger.propagate = False
logging.basicConfig()


class ThemeEditorDockWidget(BaseDockWidget):
    themeChanged = QtCore.Signal(bool, name="configChanged")

    def __init__(self, themeName, themeColor, parent=None):
        super(ThemeEditorDockWidget, self).__init__(
            themeName=themeName, themeColor=themeColor, parent=parent
        )
        self.setWindowTitle("Edit Theme:")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setTheme((themeName, themeColor))
        self.widget = BaseWidget(themeName=themeName, themeColor=themeColor)
        self.widget.setTheme((themeName, themeColor))
        self.mainLayout = QtWidgets.QVBoxLayout(self.widget)

        data = t_factory.fromJSON(self.themeName, self.themeColor)
        self._data = {}
        for entry, value in data.items():
            subLayout = QtWidgets.QHBoxLayout()

            label = QtWidgets.QLabel(entry)
            if entry == "fontFamily":
                input = QtWidgets.QComboBox()
                for f in QtGui.QFontDatabase().families():
                    input.addItem(f)

                for f in QtGui.QFontDatabase().families():
                    if f == value:
                        input.setCurrentText(f)
                        break

            elif entry.endswith("Size"):
                input = QtWidgets.QSpinBox()
                input.setValue(int(value.replace("px", "")))

            elif entry.endswith("Color"):
                input = QtWidgets.QLineEdit()
                input.setText(value)

                colorPicker = QtWidgets.QPushButton("Pick")
                colorPicker.clicked.connect(partial(self._changeColor, input))
                subLayout.addWidget(colorPicker)

            elif entry in (
                "level00",
                "level01",
                "level02",
                "level03",
                "level04",
                "hiLight",
            ):
                input = QtWidgets.QLineEdit()
                input.setText(value)

                colorPicker = QtWidgets.QPushButton("Pick")
                colorPicker.clicked.connect(partial(self._changeColor, input))
                subLayout.addWidget(colorPicker)
            else:
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

    def _changeColor(self, input):
        self.w = QtWidgets.QColorDialog()
        self.w.setCurrentColor(input.text())
        self.w.exec_()
        input.setText(str(self.w.currentColor().name()))

        print("Widget: %s", input)

    def _saveConfig(self):
        data = {}
        for k, v in self._data.items():
            if k == "fontFamily":
                data[k] = v.currentText()
            elif k.endswith("Size"):
                data[k] = "{}px".format(v.value())
            else:
                data[k] = v.text()

        t_factory.toJSON(data, self.themeName, self.themeColor)
        self.themeChanged.emit(True)
        self.setTheme((self.themeName, self.themeColor))
        self.widget.setTheme((self.themeName, self.themeColor))


if __name__ == "__main__":
    qtapp = QtWidgets.QApplication(sys.argv)
    win = ThemeEditorDockWidget(themeName="core", themeColor="")
    win.show()
    sys.exit(qtapp.exec_())
