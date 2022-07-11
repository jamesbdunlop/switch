import sys
import logging
from PySide2 import QtWidgets, QtCore
from functools import partial
from services import configManger as ss_configManager
from widgets import configBrowser as suiw_configBrowser
from widgets.base import BaseWidget
from widgets.utils import createLabeledInput
from widgets.schema import SchemaWidget
from widgets.addFolderLayout import AddFolderLayout
from widgets.previewSchema import PreviewTreeWidget

logger = logging.getLogger(__name__)
logger.propagate = False
logging.basicConfig()


class CreateSchemaWidget(BaseWidget):
    def __init__(self, themeName, themeColor, parent=None):
        super(CreateSchemaWidget, self).__init__(themeName=themeName, themeColor=themeColor, parent=parent)
        self.setWindowTitle("Schema Folder Creator")
        self._names = list()
        self._schTableWidgets = list()
        self._mainLayout = QtWidgets.QVBoxLayout(self)

        mainPropertiesWidget = QtWidgets.QGroupBox()
        mainPropertiesWidget.setTitle("Project Data:")
        mainPropertiesLayout = QtWidgets.QVBoxLayout(mainPropertiesWidget)

        gridlayout, self._projectNameInput = createLabeledInput("{:18}".format("projectName"), "Type the name of your project here.", toolTip="This is a regular string name with no spaces for your project where\nthe folders will be created.")
        mainPropertiesLayout.addLayout(gridlayout)

        gridlayout, self._projectPathInput = createLabeledInput("{:19}".format("projectPath"), "Type the path to your project. eg: E:/3D_Projects/projects", toolTip="Path to the root folder where you want to create projects.")
        mainPropertiesLayout.addLayout(gridlayout)

        gridlayout, self._projectRootName = createLabeledInput("{:16}".format("baseFolderName"), "Type the name of the base folder to make under the project. eg: Character / Props / etc.", toolTip="drive:/projectpath/projectName/baseFolder/schema..")
        mainPropertiesLayout.addLayout(gridlayout)

        schemaWidget = QtWidgets.QGroupBox()
        schemaWidget.setTitle("Create Schema: ")
        gbLayout = QtWidgets.QVBoxLayout(schemaWidget)

        scroller = QtWidgets.QScrollArea()
        scroller.setWidget(schemaWidget)
        scroller.setWidgetResizable(True)

        # Always add ROOTS and SCHEMA
        self.schemaLayout = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        gbLayout.addWidget(self.schemaLayout)
        self.rootsTableWidget = self._createFolderTableSetup("ROOTS")
        self.baseFoldersTableWidget = self._createFolderTableSetup("BASEFOLDERS")
        self.schemaLayout.addWidget(self.rootsTableWidget)
        self.schemaLayout.addWidget(self.baseFoldersTableWidget)

        buttonLayout = QtWidgets.QHBoxLayout()
        loadButton = QtWidgets.QPushButton(self._fetchIcon("iconmonstr-login-icon-256"), "Load Existing Config/Template")
        loadButton.clicked.connect(self._loadSchema)

        saveToButton = QtWidgets.QPushButton(self._fetchIcon("iconmonstr-save-1-240"), "Save Schema")
        saveToButton.clicked.connect(self._saveSchema)

        buttonLayout.addWidget(loadButton)
        buttonLayout.addWidget(saveToButton)

        buttonLayout2 = QtWidgets.QHBoxLayout()
        addToButton = QtWidgets.QPushButton(self._fetchIcon("iconmonstr-plus-1-240"), "Add SubFolder Schema")
        addToButton.clicked.connect(self._addFolderLayout)

        previewToButton = QtWidgets.QPushButton(self._fetchIcon("iconmonstr-plus-1-240"), "Preview Schema")
        previewToButton.clicked.connect(self._createPreview)
        buttonLayout2.addWidget(addToButton)
        buttonLayout2.addWidget(previewToButton)

        self._mainLayout.addWidget(mainPropertiesWidget)
        self._mainLayout.addLayout(buttonLayout)
        self._mainLayout.addWidget(scroller)
        self._mainLayout.addLayout(buttonLayout2)

        self.resize(1400, 600)

    def _nameExists(self, name):
        return name in self._names

    def _addFolderLayout(self):
        """Pop up a UI to allow a user to input a name for a new subFolder layout
        """
        self.ui = AddFolderLayout(self.themeName, self.themeColor)
        self.ui.name.connect(self._createFolderTableSetup)
        self.ui.show()

    def _schemaWidgetClosed(self, widgetName):
        """Checks if user wants to close the widget when toggling the QGroupBox title.

        Args:
            widget (string): the QGroupBox widget.
        """
        self._names.remove(widgetName)
        # Replace any values that used that table wigdet's name
        for i, tableWidget in enumerate(self._schTableWidgets):
            count = tableWidget.table().rowCount()
            if not count:
                continue

            for idx in range(count):
                value = tableWidget.table().item(idx, 1).text()
                if value == widgetName:
                    tableWidget.table().item(idx, 1).setText("None")

        # Make sure it no longer exists in tables
        for widget in self._schTableWidgets:
            if widget.name() == widgetName:
                logger.debug("Removing %s from self._schTableWidgets.", widget.name())
                self._schTableWidgets.remove(widget)
                del widget

        logger.debug("Successfully removed %s", widgetName)

    def _createFolderTableSetup(self, name):
        """Creates the layout for the folderSchema creators.

        Args:
            name (string):
        """
        if self._nameExists(name):
            logger.debug("SubFolder name already exists! %s", name)
            return None, None

        schemaWidget = SchemaWidget(name, self.themeName, self.themeColor, parent=self)
        schemaWidget.closed.connect(self._schemaWidgetClosed)

        self.schemaLayout.addWidget(schemaWidget)
        sizes = [5] * self.schemaLayout.count()
        sizes[0] = 1
        self.schemaLayout.setSizes(sizes)

        self._names.append(name)
        self._schTableWidgets.append(schemaWidget)
        return schemaWidget

    def createConfigData(self):
        """Creates a dict of the schema data from the widgets etc

        Returns:
            dict
        """
        data = dict()
        data["projectName"] = self._projectNameInput.text()
        data["projectPath"] = self._projectPathInput.text()
        data["configRoot"] = self._projectRootName.text()
        for i, tableWidget in enumerate(self._schTableWidgets):
            logger.debug("Saving data for %s", tableWidget.name())
            foldername = tableWidget.name()
            data[foldername] = dict()
            count = tableWidget.table().rowCount()
            if not count:
                continue

            for idx in range(count):
                key = tableWidget.table().item(idx, 0).text()
                value = tableWidget.table().item(idx, 1).text()
                logger.debug("\t\tkey: %s | value: %s", key, value)
                if isinstance(value, str) and value == "None":
                    data[foldername][key] = None
                else:
                    data[foldername][key] = value

        return data

    def _saveSchema(self):
        """Parse the wigets and save the data to json
        """
        data = self.createConfigData()
        self.configBrowser = suiw_configBrowser.ConfigBrowser(self.themeName, self.themeColor, toSave=True)
        self.configBrowser.fileSelected.connect(partial(self._toJSON, data=data))
        self.configBrowser.show()

    def _toJSON(self, filepath, data):
        """Clean up the filePath returned from the dialog and send through to the save config.

        Args:
            filepath (string): Filename selected from the dialog
            data (dict): The parsed UI data from the widgets
        """
        ss_configManager.saveConfig(filepath=filepath, data=data)

    def _loadSchema(self):
        """

        Returns:
        """
        self.configBrowser = suiw_configBrowser.ConfigBrowser(self.themeName, self.themeColor)
        self.configBrowser.show()
        self.configBrowser.fileSelected.connect(self._fromJSON)

    def _fromJSON(self, filepath):
        """Creates the layout from an existing config.json

        Args:
            filepath (string):
        """
        logger.debug("Loading: %s", filepath)
        for x in range(self.schemaLayout.count()):
            w = self.schemaLayout.widget(x)
            w.close()

        self._schTableWidgets = list()
        self._names = list()

        config = ss_configManager.getConfigByFilePath(filepath)
        if config is None:
            logger.error("Failed to load the config!")
            return

        configData = config.data
        self._projectNameInput.setText(configData.get("projectName", ""))
        self._projectPathInput.setText(configData.get("projectPath", ""))
        self._projectRootName.setText(configData.get("configRoot", ""))

        ignore = ("projectName", "projectPath", "configRoot")
        for folderStructureName, data in configData.items():
            if folderStructureName in ignore:
                continue

            logger.debug("folderStructureName: %s", folderStructureName)
            schemaTableWidget = self._createFolderTableSetup(folderStructureName)
            for folderName, subFolder in data.items():
                schemaTableWidget.addToTable([folderName, str(subFolder)])

    def _createPreview(self):
        data = self.createConfigData()
        config = ss_configManager.Config(data)
        self.previewUI = PreviewTreeWidget(themeName="core", themeColor="", config=config, parent=None)
        self.previewUI.show()

    def iterSchemaWidgets(self):
        for widget in self._schTableWidgets:
            yield widget


if __name__ == "__main__":
    qtapp = QtWidgets.QApplication(sys.argv)
    win = CreateSchemaWidget(themeName="core", themeColor="")
    win.show()
    sys.exit(qtapp.exec_())
