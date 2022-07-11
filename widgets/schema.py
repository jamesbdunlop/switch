import sys
import logging
from functools import partial
from PySide2 import QtWidgets, QtCore
from widgets.base import BaseWidget as BaseWidget, ThemeMixin
from widgets.addFolderPairToTable import AddFolderPairToTable
from widgets.addFolderLayout import AddFolderLayout

logger = logging.getLogger(__name__)
logger.propagate = False
logging.basicConfig()


class RenameableGroupBox(ThemeMixin, QtWidgets.QGroupBox):
    rename = QtCore.Signal(str, name="rename")

    def __init__(self, themeName=None, themeColor=None, parent=None):
        """

        Args:
            themeName (string):
            themeColor (string):
            parent (QtWidget):
        """
        QtWidgets.QGroupBox.__init__(self, parent=parent)
        ThemeMixin.__init__(self, themeName=themeName, themeColor=themeColor)

    def mouseDoubleClickEvent(self, e):
        """Pops up a UI to rename the QGroupBox and therefore the folder schema.

        Args:
            e (QEvent):
        """
        QtWidgets.QGroupBox.mouseDoubleClickEvent(self, e)
        if self.title()[:-2] in ("ROOTS", "BASEFOLDERS"):
            return

        ui = AddFolderLayout(self.themeName, self.themeColor)
        ui.name.connect(self._commitRename)
        ui.setWindowTitle("RENAME: {} to..".format(self.title()))
        ui.show()
        ui.setStyleSheet(self.sheet)

    def _commitRename(self, name):
        """The method to do the rename from the popup ui.

        Args:
            name (string): The name we're changing to.
        """
        self.rename.emit(name)


class SchemaWidget(BaseWidget):
    closed = QtCore.Signal(str, name="closed")

    def __init__(self, name, themeName, themeColor, parent=None):
        """

        Args:
            name (string): The name for the folder schema
            themeName (string):
            themeColor (string):
            parent QtWidget:
        """
        BaseWidget.__init__(self, themeName=themeName, themeColor=themeColor, parent=parent)
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self._name = name

        self.gbWidget = RenameableGroupBox(self.themeName, self.themeColor)
        self.gbWidget.rename.connect(self._rename)
        self.gbWidget.setTitle("{}: ".format(name))

        self.gbLayout = QtWidgets.QVBoxLayout(self.gbWidget)

        self._tableWidget = QtWidgets.QTableWidget()
        self._tableWidget.setRowCount(0)
        self._tableWidget.setColumnCount(2)
        self._tableWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self._tableWidget.customContextMenuRequested.connect(self._rcMenu)

        headerView = QtWidgets.QHeaderView(QtCore.Qt.Horizontal, self._tableWidget)
        headerView.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self._tableWidget.setHorizontalHeader(headerView)
        self._tableWidget.setHorizontalHeaderLabels(["FolderName", "SubFolderSchema"])

        self.gbLayout.addWidget(self._tableWidget)

        # Additonal buttons..
        buttonLayout = QtWidgets.QHBoxLayout()
        addButton = QtWidgets.QPushButton(self._fetchIcon("iconmonstr-plus-1-240"), "Add")
        addButton.clicked.connect(self._addFolderPairToTableUI)
        addButton.setToolTip("Add folder to schema.")

        removeButton = QtWidgets.QPushButton(self._fetchIcon("iconmonstr-minus-4-240"), "Rem")
        removeButton.clicked.connect(self._removeRows)
        removeButton.setToolTip("Remove selected rows from schema.")

        buttonLayout.addWidget(addButton)
        buttonLayout.addWidget(removeButton)

        toIgnoreForCheckable = ("ROOTS", "BASEFOLDERS")
        if name not in toIgnoreForCheckable:
            closeButton = QtWidgets.QPushButton(self._fetchIcon("iconmonstr-x-mark-4-240"), "")
            closeButton.clicked.connect(partial(self._close, widget=self.gbWidget))
            closeButton.setMaximumWidth(32)
            closeButton.setToolTip("Remove this schema entirely.")
            buttonLayout.addWidget(closeButton)

        self.mainLayout.addWidget(self.gbWidget)
        self.mainLayout.addLayout(buttonLayout)
        self.resize(200, 100)

    def _rcMenu(self, point):
        """The right click menu for the table. It will make actions out of the valid schema folder names

        Args:
            point (QPoint): This comes in from the contextMenu
        """
        selected = self.table().selectedItems()
        editColumn = selected[0].column()
        if editColumn == 0:
            return

        # This is prone to failing if you run isolated testing on this widget.
        self.menu = QtWidgets.QMenu()
        self.menu.setTitle("Actions:")
        self.menu.setWindowTitle("rcMenu")

        parent = self.nativeParentWidget().widget
        for name in parent._names:
            if name == self.name():
                continue
            action = self.menu.addAction(name)
            action.triggered.connect(partial(self._setData, name))

        action = self.menu.addAction("None")
        action.triggered.connect(partial(self._setData, "None"))

        self.menu.setStyleSheet(self.sheet)
        self.menu.move(self.mapToGlobal(point))
        self.menu.show()

    def _setData(self, name):
        """Sets the col[1] to be that of the title() from one of the other schema widgets.

        Args:
            name(string): The name from one of the other widgets to use.
        """
        selected = self.table().selectedItems()
        editColumn = selected[0].column()
        if editColumn == 0:
            return

        selected[0].setText(name)

    def _rename(self, name):
        """Renames the schema widget and sets the groupBox title
        """
        self._name = name
        self.gbWidget.setTitle(self._name)

    def _removeRows(self):
        """Removes the selected rows
        """
        selected = self.table().selectedItems()
        start = selected[0].row()
        end = selected[-1].row()
        for x in range((end-start)+1):
            self.table().removeRow(end)
            end -= 1

    def addToTable(self, data):
        """Set the data from the AddFolderPairToTable widget

        Args:
            data (list[tableWidget, string, string, QTableWidget):
        """
        folderName, subFolderName = data

        qtwiFolderName = QtWidgets.QTableWidgetItem(text=folderName, type=QtCore.Qt.DisplayRole)
        qtwiFolderName.setData(QtCore.Qt.DisplayRole, folderName)

        qtwiSubFolderName = QtWidgets.QTableWidgetItem(text=subFolderName, type=QtCore.Qt.DisplayRole)
        qtwiSubFolderName.setData(QtCore.Qt.DisplayRole, subFolderName)

        # Set basic row count to see stuff..
        count = self.table().rowCount()
        if count == 0:
            self.table().setRowCount(1)
        else:
            self.table().setRowCount(count+1)

        emptyRow = 0
        for i in range(self.table().rowCount()):
            existing = self.table().item(i, 0)
            if existing is None:
                emptyRow = i

        self.table().setItem(emptyRow, 0, qtwiFolderName)
        self.table().setItem(emptyRow, 1, qtwiSubFolderName)

    def _addFolderPairToTableUI(self):
        """Pops up a UI to add the folderName / subFolderName pairing.

        Args:
            table (QTableWidget):
        """
        self.pairUI = AddFolderPairToTable(self.themeName, self.themeColor)
        self.pairUI.folderPair.connect(self.addToTable)
        self.pairUI.show()

    def _close(self, widget):
        """Checks if user wants to close the widget when toggling the QGroupBox title.

        Args:
            widget (QGroupBox): the QGroupBox widget.
        """
        confirm = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Delete?!",
                                        "Delete this folder schema?",
                                        QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel, None,
                                        QtCore.Qt.WindowStaysOnTopHint)
        confirm.setStyleSheet(self.sheet)
        if confirm.exec_() != QtWidgets.QMessageBox.Ok:
            widget.setChecked(False)
            return

        self.closed.emit(self.name())
        self.close()

    def name(self):
        """The scheme name. Can be see via the title.
        Returns:
            string
        """
        return self._name

    def table(self):
        """The table widget with the folder names in it.

        Returns:
            QTableWidgets
        """
        return self._tableWidget


if __name__ == "__main__":
    qtapp = QtWidgets.QApplication(sys.argv)
    win = SchemaWidget(name="test", themeName="core", themeColor="")
    win.show()
    sys.exit(qtapp.exec_())
