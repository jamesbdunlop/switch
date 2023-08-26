import sys
import logging
from PySide2 import QtWidgets, QtCore, QtGui
from functools import partial
from constants import schema as c_schema
from services import configManger as ss_configManager
from widgets import configBrowser as suiw_configBrowser
from widgets.base import BaseWidget
from widgets.base import ThemeMixin
from widgets.utils import createLabeledInput
from widgets.utils import errorWidget
from widgets.schema import SchemaWidget
from widgets.addFolderLayout import AddFolderLayout

logger = logging.getLogger(__name__)
logger.propagate = False
logging.basicConfig()


class CreateSchemaWidget(BaseWidget):
    def __init__(self, themeName, themeColor, parent=None):
        super(CreateSchemaWidget, self).__init__(
            themeName=themeName, themeColor=themeColor, parent=parent
        )
        self.setWindowTitle("Schema Folder Creator")
        self.setObjectName("SchemaFolderCreator")
        self.setTheme([themeName, themeColor])

        self._names = list()
        self._schTableWidgets = list()
        self._mainLayout = QtWidgets.QVBoxLayout(self)

        # Always add ROOTS and SCHEMA
        self.schemaTree = SchemaTreeWidget(self.themeName, self.themeColor)

        mainPropertiesWidget = QtWidgets.QGroupBox()
        mainPropertiesWidget.setTitle("Project Data:")
        mainPropertiesLayout = QtWidgets.QVBoxLayout(mainPropertiesWidget)

        gridlayout, self._projectPathInput = createLabeledInput(
            "{:19}".format("projectPath"),
            "Type the path to your project. eg: E:/3D_Prints",
            toolTip="PROJECTPATH/projectName/baseFolder/**schemaCreationHere \n PROJECTPATH should include the drive.",
        )
        mainPropertiesLayout.addLayout(gridlayout)
        
        gridlayout, self._projectNameInput = createLabeledInput(
            "{:18}".format("projectName"),
            "Type the name of your project here. eg: anycubicUltra",
            toolTip="projectPath/PROJECTNAME/projectRoot/**schemaCreationHere \n eg: E:/3D_Prints/anycubicUltra",
        )
        mainPropertiesLayout.addLayout(gridlayout)

        gridlayout, self._projectRootName = createLabeledInput(
            "{:16}".format("projectRootFolderName"),
            "Root folder name. eg: modelPrep",
            toolTip="projectPath/projectName/PROJECTROOT/**schemaCreationHere \n eg: E:/3D_Prints/anycubicUltra/modelPrep",
        )
        mainPropertiesLayout.addLayout(gridlayout)
        self._projectRootName.textChanged.connect(self.schemaTree.setConfigRootName)

        gridlayout, self._projectExtensions = createLabeledInput(
            "{:16}".format("projectFileExensions"),
            "Comma sep list of extensions.",
            toolTip="eg: .ma, .mb, .obj, .png, .txt",
        )
        mainPropertiesLayout.addLayout(gridlayout)

        schemaGBWidget = QtWidgets.QGroupBox()
        schemaGBWidget.setTitle("Create Schema: ")
        gbLayout = QtWidgets.QVBoxLayout(schemaGBWidget)
        gbLayout.addWidget(self.schemaTree)

        scroller = QtWidgets.QScrollArea()
        scroller.setWidget(schemaGBWidget)
        scroller.setWidgetResizable(True)

        buttonLayout = QtWidgets.QHBoxLayout()
        loadButton = QtWidgets.QPushButton(
            self._fetchIcon("iconmonstr-login-icon-256"),
            "Load Existing Config/Template",
        )
        loadButton.clicked.connect(self._loadSchema)

        saveToButton = QtWidgets.QPushButton(
            self._fetchIcon("iconmonstr-save-1-240"), "Save Schema"
        )
        saveToButton.clicked.connect(self._saveSchema)

        previewToButton = QtWidgets.QPushButton(
            self._fetchIcon("iconmonstr-plus-1-240"), "Preview Schema"
        )
        previewToButton.clicked.connect(self._createPreview)

        buttonLayout.addWidget(loadButton)
        buttonLayout.addWidget(saveToButton)
        buttonLayout.addWidget(previewToButton)

        self._mainLayout.addLayout(buttonLayout)
        self._mainLayout.addWidget(mainPropertiesWidget)
        self._mainLayout.addWidget(scroller)

        self.resize(1400, 600)
    
    def _createPreview(self):
        data = self._parseTreeData()
        config = ss_configManager.Config(data)
        self.previewUI = SchemaTreeWidget(
            themeName="core", themeColor="", asPreview=True, config=config, parent=None
        )
        self.previewUI.setConfigRootName(config.configRoot())
        self.previewUI.show()

    def _saveSchema(self):
        """Parse the wigets and save the data to json"""
        data = self._parseTreeData()
        self.configBrowser = suiw_configBrowser.ConfigBrowser(
            self.themeName, self.themeColor, toSave=True
        )
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
        self.configBrowser = suiw_configBrowser.ConfigBrowser(
            self.themeName, self.themeColor
        )
        self.configBrowser.show()
        self.configBrowser.fileSelected.connect(self._fromJSON)

    def _parseTreeData(self):
        projName = self._projectNameInput.text()
        projPath = self._projectPathInput.text()
        projRoot = self._projectRootName.text()
        projExt = [n.lstrip() for n in self._projectExtensions.text().split(",")]
        if not projName or not projPath or not projRoot:
            msg = "You must set a the project settings!"
            logger.error(msg)
            errorWidget("Warning:", msg)
            return
        
        data = self.schemaTree._parseTreeToData()
        data["projectName"] = projName
        data["projectPath"] = projPath
        data["configRoot"] = projRoot
        data["validExt"] = projExt

        return data

    def _fromJSON(self, filepath):
        """Creates the layout from an existing config.json

        Args:
            filepath (string):
        """
        logger.debug("Loading: %s", filepath)

        config = ss_configManager.getConfigByFilePath(filepath)
        if config is None:
            logger.error("Failed to load the config!")
            return

        self._projectNameInput.setText(config.data.get("projectName", ""))
        self._projectPathInput.setText(config.data.get("projectPath", ""))
        self._projectRootName.setText(config.data.get("configRoot", ""))
        extensions = config.data.get("validExt", "")
        extStr = ""
        for idx, n in enumerate(extensions):
            if idx == len(extensions)-1:
                extStr += n
            else:
                extStr += "%s, " % n
        self._projectExtensions.setText(extStr)

        self.schemaTree.setConfig(config)
        self.schemaTree._refresh()


class SchemaTreeWidget(QtWidgets.QTreeWidget, ThemeMixin):
    def __init__(self, themeName, themeColor, asPreview=False, config=None, parent=None):
        QtWidgets.QTreeWidget.__init__(self, parent=parent)
        ThemeMixin.__init__(self, themeName=themeName, themeColor=themeColor)
        self.setWindowTitle("Schema Create....")
        self.setObjectName("SchemaTreeWidget")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setTheme([themeName, themeColor])
        self.setStyleSheet(self.sheet)
        self.setColumnCount(1)
        self.setHeaderLabels(["Folder Schema"])
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._customRCMenu)
        self.itemPressed.connect(self._closeEditors)
        self.resize(400, 600)

        self.previousValue = None
        self.asPreview = asPreview
        self._config = config if config is not None else ss_configManager.Config(data=c_schema.EMPTY_CONFIG_DATA)
        
        self.createTreeProjectRoot()
        self.createTreeSchemaRoots()
        self.createTreeSchemaBases()
        if not self.asPreview:
            self.createTreeSchemaLinked()

   
    ### SETTERS / GETTERS
    def config(self):
        return self._config
    
    def setConfig(self, config):
        self._config = config
        self.clear()
        self.createTreeProjectRoot()

    def isValidConfig(self):
        if self.config() is None:
            logger.info("Nothing to update for root; skipping...")
            return False
        return True

    def configRootName(self):
        return self._projectRoot.text(0)
    
    def setConfigRootName(self, name):
        self._projectRoot.setText(0, name)

    def _refresh(self):
        self._projectRoot.setText(0, self.config().configRoot())
        self.createTreeSchemaRoots()
        self.createTreeSchemaBases()
        self.createTreeSchemaLinked()

    def _customRCMenu(self, *args):
        """ Creates the right click menu """
        self._menu = QtWidgets.QMenu(self)
        currentItem = self.currentItem()
        # We leave all rootFolders alone as they have a single dynAsset under them
        rowName = currentItem.text(0)
        if self._isRootFolderItem(currentItem) or rowName == 'None':
            removeAction = self._menu.addAction("Remove Subfolder")
            removeAction.triggered.connect(self._removeSubfolder)

        if rowName != 'None' and not self._isRootFolderItem(currentItem):
            addAction = self._menu.addAction("Add Folder")
            addAction.triggered.connect(self._addSubfolderPopUp)
            
            if not self._isTopLevelItem(currentItem) and currentItem.text(0) != c_schema.DYN_ASSET_NAME:
                removeAction = self._menu.addAction("Remove Folder")
                removeAction.triggered.connect(self._removeSubfolder)

                # TO DO GET LINKED TO SHOW ONLY APPROPRIATE LINK MENUS
                linkToMenu = self._menu.addMenu("LinkTo")
                validLinkedFolderNames = []
                # Check the current item is a linkedSubFolderItem
                if self._isLinkedSubFolderChild(currentItem):
                    if currentItem.text(0) in self.config().linkedFolderNames():
                        parentLinkedSubFolderName = currentItem.text(0)
                    else:
                        parentLinkedSubFolderName = self._getLinkedParentName(currentItem)

                    for linkedFolderName in self.config().linkedFolderNames():
                        invalid = False
                        if linkedFolderName != parentLinkedSubFolderName:
                            # Now make sure we don't have a child of that name in the linked grp to avoid cycles
                            twi = self._getLinkedSubFolderTWI(linkedFolderName)
                            for child in self.iterHrc(twi):
                                if child.text(0) == parentLinkedSubFolderName:
                                    invalid = True
                                    break

                            if not invalid:
                                validLinkedFolderNames.append(linkedFolderName)
                else:
                    validLinkedFolderNames = self.config().linkedFolderNames()
                for validLinked in validLinkedFolderNames:
                    action = linkToMenu.addAction(validLinked)
                    action.triggered.connect(partial(self._addLinked, validLinked))

        self._menu.move(QtGui.QCursor().pos())
        self._menu.show()

    def _childExists(self, twi, name):
        childCount = twi.childCount()
        for idx in range(childCount):
            child = twi.child(idx)
            if child.text(0) == name:
                return True
        return False
    
    def _getLinkedSubFolderTWI(self, name):
        for twi in self.iterLinkedSubFolderItems():
            if twi.text(0) == name:
                return twi

    ## TREE ITERS
    def iterTopLevelItems(self):
        topLvlCount = self.topLevelItemCount()
        for x in range(topLvlCount):
            yield self.topLevelItem(x)
    
    def iterRootItems(self):
        # Find the actual projectRoot, then iter for it's children
        # ignoring the linkedFolder entries.
        for tli in self.iterTopLevelItems():
            if tli.text(0) == c_schema.SUBFOLDER_TITLE_NAME:
                continue
            childCount = tli.childCount()
            for idx in range(childCount):
                yield tli.child(idx)
    
    def iterBaseItems(self):
        # Children of the dynamic asset entries for all roots.
        for rootItem in self.iterRootItems():
            dynAsset = rootItem.child(0)
            childCount = dynAsset.childCount()
            for idx in range(childCount):
                yield dynAsset.child(idx)

    def iterLinkedSubFolderItems(self):
        # Children of the linkedSubFolder root.
        for tli in self.iterTopLevelItems():
            if tli.text(0) != c_schema.SUBFOLDER_TITLE_NAME:
                continue
            
            childCount = tli.childCount()
            for idx in range(childCount):
                yield tli.child(idx)

    def iterHrc(self, twi):
        childCount = twi.childCount()
        if not childCount:
            yield twi
        
        for idx in range(childCount):
            child = twi.child(idx)
            yield child

            subChildCount = child.childCount()
            if subChildCount:
                for c in self.iterHrc(child):
                    yield c
        
    ## INTERNAL GETTERS
    def _isTopLevelItem(self, twi):
        allToLevelItems = list(self.iterTopLevelItems())
        return twi in allToLevelItems

    def _isRootFolderItem(self, twi):
        allRootItems = list(self.iterRootItems())
        return twi in allRootItems
    
    def _isBaseFolderItem(self, twi):
        allBaseItems = list(self.iterBaseItems())
        return twi in allBaseItems

    def _isSubFolderTopLevelItem(self, twi):
        if twi.text(0) == c_schema.SUBFOLDER_TITLE_NAME:
            return True
        
        return False
    
    def _isLinkedSubFolderItem(self, twi):
        allLinkedItems = self.iterLinkedSubFolderItems()
        return twi in allLinkedItems
    
    def _isLinkedSubFolderItemName(self, twiName):
        allLinkedItemNames = [n.text(0) for n in self.iterLinkedSubFolderItems()]
        return twiName in allLinkedItemNames

    def _isLinkedSubFolderChild(self, twi):
        parent = twi.parent()
        while parent:
            if parent.text(0) == c_schema.SUBFOLDER_TITLE_NAME:
                return True
            else:
                parent = parent.parent()

    def _getLinkedParentName(self, twi):
        parent = twi.parent()
        while parent:
            if parent.text(0) == c_schema.SUBFOLDER_TITLE_NAME:
                return twi.text(0)
        return ""

    ## MUTATE TREE
    def createTreeProjectRoot(self):
        """ Create the top level root item and set an invalid name, this will be updated on refresh. """
        if not self.isValidConfig():
            return
        self._projectRoot = QtWidgets.QTreeWidgetItem()
        self._projectRoot.setText(0, c_schema.INVALID_ROOTNAME)
        self.addTopLevelItem(self._projectRoot)
    
    def createTreeSchemaRoots(self):
        if not self.isValidConfig():
            return
        
        for rootName in self.config().iterRoots():
            rootTWI = QtWidgets.QTreeWidgetItem()
            rootTWI.setText(0, rootName)
            self._projectRoot.addChild(rootTWI)

            ## TEMP ASSET NAME - READ ONLY as this changes on creation in the main UI
            self._createReadOnlyDynamicEntry(rootTWI)
    
    def createTreeSchemaBases(self):
        if not self.isValidConfig():
            return
        
        def expandLinkedFolders(twi, folderName):
            data = self.config().getLinkedSubFolder(folderName)
            for parentFolderName, subFolders in data.items():
                if parentFolderName in self.config().linkedFolderNames():
                    expandLinkedFolders(twi, parentFolderName)
                else:
                    parentTWI = QtWidgets.QTreeWidgetItem()
                    parentTWI.setText(0, parentFolderName)
                    twi.addChild(parentTWI)
                
                for subFolder in subFolders:
                    if subFolder in self.config().linkedFolderNames():
                        expandLinkedFolders(parentTWI, subFolder)
                    else:
                        if subFolder == None or subFolder == str(None):
                            continue

                        subFolderTWI = QtWidgets.QTreeWidgetItem()
                        subFolderTWI.setText(0, subFolder)
                        parentTWI.addChild(subFolderTWI)

        for rootItem in self.iterRootItems():
            dynAsset = rootItem.child(0)

            for baseName, linkedData in self.config().iterBaseFolders():
                if baseName == None or baseName == str(None):
                    continue

                baseTWI = QtWidgets.QTreeWidgetItem()
                baseTWI.setText(0, baseName)
                dynAsset.addChild(baseTWI)
                for childName in linkedData:
                    if childName == None or childName == str(None):
                        continue
                    
                    if self.asPreview and childName in self.config().linkedFolderNames():
                        expandLinkedFolders(baseTWI, childName)
                    else:
                        # just show the linked name
                        childTWI = QtWidgets.QTreeWidgetItem()
                        childTWI.setText(0, childName)
                        baseTWI.addChild(childTWI)

    def createTreeSchemaLinked(self):
        subFolderTLI = QtWidgets.QTreeWidgetItem()
        subFolderTLI.setText(0, c_schema.SUBFOLDER_TITLE_NAME)
        self.addTopLevelItem(subFolderTLI)
        
        for linkedIdName in self.config().linkedFolderNames():
            # PARENT LINKED FOLDER NAME
            if linkedIdName == None or linkedIdName == str(None):
                continue
            subFolderRoot = QtWidgets.QTreeWidgetItem()
            subFolderRoot.setText(0, linkedIdName)
            subFolderTLI.addChild(subFolderRoot)
            
            # CHILD FOLDERS AND THEIR LINKS/FOLDERS
            data = self.config().getLinkedSubFolder(linkedIdName)
            for subFolderName, folders in self.config().iterLinkedSubFolderData(data):
                if subFolderName == None or subFolderName == str(None):
                    continue
                subFolder = QtWidgets.QTreeWidgetItem()
                subFolder.setText(0, str(subFolderName))
                subFolderRoot.addChild(subFolder)
                for linkedFolderName in folders:
                    if linkedFolderName == None or linkedFolderName == str(None):
                        continue
                    linkedFolder = QtWidgets.QTreeWidgetItem()
                    linkedFolder.setText(0, str(linkedFolderName))
                    subFolder.addChild(linkedFolder)

    def _createReadOnlyDynamicEntry(self, parent):
        """ Creates the dynamic asset entry that would be created by the user adding a folder via the ui."""
        dynamicAssetTWI = QtWidgets.QTreeWidgetItem()
        dynamicAssetTWI.setText(0, c_schema.DYN_ASSET_NAME)
        parent.addChild(dynamicAssetTWI)
        return dynamicAssetTWI

    def _removeSubfolder(self):
        parent = self.currentItem().parent()
        if parent is None:
            return
        index = parent.indexOfChild(self.currentItem())
        parent.takeChild(index)

    def _addToMatchingBaseFolder(self, currentItem, folderName):
        if self._isLinkedSubFolderChild(currentItem):
            return
        
        for eachItem in self._findTreeWidgetItemsByName(currentItem.text(0)):
            if eachItem == currentItem:
                continue
            
            if self._childExists(eachItem, folderName):
                return
            
            dupChild = QtWidgets.QTreeWidgetItem()
            dupChild.setText(0, folderName)
            eachItem.addChild(dupChild)

    def _addSubfolderByName(self, folderName):
        """Add child of name to the self.currentItem() row. 

        Args:
            folderName (string): String name for the folder
        """
        isSubFolderChild = self._isSubFolderTopLevelItem(self.currentItem())
        if isSubFolderChild:
            folderName = folderName.upper()
        child = QtWidgets.QTreeWidgetItem()
        child.setText(0, folderName)
        
        self.currentItem().addChild(child)

        isTopLvl = self._isTopLevelItem(self.currentItem())
        if isTopLvl and not isSubFolderChild:
            self._createReadOnlyDynamicEntry(child)
        self._addToMatchingBaseFolder(self.currentItem(), folderName)

    def _addSubfolderPopUp(self):
        """ Fire the UI to enter a new folder name """
        # We don't ever add to a None entry!!
        if self.currentItem().text(0) == 'None':
            return
        
        folderName = AddFolderLayout(self.themeName, self.themeColor)
        folderName.show()
        folderName.name.connect(self._addSubfolderByName)
    
    def _addLinked(self, folderSchemaName):
        # We don't ever add to a None entry!!
        if self.currentItem().text(0) == 'None':
            return
        
        if self._childExists(self.currentItem(), folderSchemaName):
            return
        
        child = QtWidgets.QTreeWidgetItem()
        child.setText(0, folderSchemaName)
        self.currentItem().addChild(child)
        self._addToMatchingBaseFolder(self.currentItem(), folderSchemaName)

    ## UI STUFF
    def mouseDoubleClickEvent(self, e):
        selectedRow = self.currentItem()
        if self._isTopLevelItem(selectedRow) or selectedRow is None or selectedRow.text(0) in c_schema.READ_ONLY_NAMES:
            return
        
        self.previousValue = selectedRow.text(0)
        self.openPersistentEditor(selectedRow, 0)

    def _closeEditors(self):
        def closeAllChildEditors(twi):
            for idx in range(twi.childCount()):
                child = twi.child(idx)
                if self.isPersistentEditorOpen(child):
                    self.closePersistentEditor(child)
                    for existing in self._findTreeWidgetItemsByName(self.previousValue):
                        existing.setText(0, self.previousValue)
                        
                closeAllChildEditors(child)

        for tlwi in self.iterTopLevelItems():
            closeAllChildEditors(tlwi)
        
    def _findTreeWidgetItemsByName(self, itemName, ignoreLinked=True):
        # My own search cause the self.findItems finds nothing. GRRR
        def iterChildren(twi, found):
            count = twi.childCount()
            for idx in range(count):
                childItem = twi.child(idx)
                if childItem.text(0) == itemName:
                    found.append(childItem)
                
                iterChildren(childItem, found)
            return found
                
       
        found = []
        for tlwi in self.iterTopLevelItems():
            if ignoreLinked and tlwi.text(0) == c_schema.SUBFOLDER_TITLE_NAME:
                continue
            
            iterChildren(tlwi, found)
            return found
        
        return found

    ## TREE TO DATA
    def _parseRoots(self, data):
        data["ROOTS"] = {}
        for rootItem in self.iterRootItems():
            data["ROOTS"][rootItem.text(0)] = None

    def _parseBaseFolders(self, data):
        data["BASEFOLDERS"] = {}
        for baseItem in self.iterBaseItems():
            subFolders = []
            for sidx in range(baseItem.childCount()):
                linked = baseItem.child(sidx)
                subFolders.append(linked.text(0))
            data["BASEFOLDERS"][baseItem.text(0)] = subFolders

    def _parseLinkedFolders(self, data):
        def parseLinkedChildren(linkedSubFolder, data):
            childCount = linkedSubFolder.childCount()          
            for idx in range(childCount):
                child = linkedSubFolder.child(idx)
                subFolders = []
                for sidx in range(child.childCount()):
                    linked = child.child(sidx)
                    subFolders.append(linked.text(0))
                data[child.text(0)] = subFolders or [None]
                # parseLinkedChildren(child, data)

        for linkedSubFolder in self.iterLinkedSubFolderItems():
            data[linkedSubFolder.text(0)] = {}
            parseLinkedChildren(linkedSubFolder, data[linkedSubFolder.text(0)])
            
    def _parseTreeToData(self):
        """ Iter the tree widget and construct a dict for use with the Config """
        data = {}
        self._parseRoots(data)
        self._parseBaseFolders(data)
        self._parseLinkedFolders(data)
        return data


if __name__ == "__main__":
    qtapp = QtWidgets.QApplication(sys.argv)
    win = CreateSchemaWidget(themeName="core", themeColor="")
    win.show()
    sys.exit(qtapp.exec_())
