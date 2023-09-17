# 2022: Author James Dunlop: james@anim83d.com

import sys, os
import logging
import time
from functools import partial
from PySide2 import QtWidgets, QtCore, QtGui
from themes import factory as st_factory
from widgets.base import IconMixin
from widgets.help import HelpView
from widgets.splash import SplashWidget
from widgets.folderDockWidget import FolderDockWidget
from widgets.configDockWidget import ConfigDockWidget
from widgets import configBrowser as suiw_configBrowser
from widgets.base import BaseDockWidget as BaseDockWidget
from widgets import systemFileBrowser as suiw_systemBrowser
from widgets.themeEditorDockWidget import ThemeEditorDockWidget
from widgets.customBrowserDockWidget import CustomBrowserDockWidget
from services import folderManager as ss_folderManager
from services import configManger as ss_configManager

insideMaya = False
try:
    from maya import cmds as cmds
    from maya.app.general import mayaMixin as mag_mayaMixin

    insideMaya = True
except ImportError:
    pass

logger = logging.getLogger(__name__)
logger.propagate = False
logging.basicConfig()

VERS = "0.1.8"
APPNAAME = "switch"
WORKSPACENAME = "switchDock"
WORKSPACEDOCKNAME = "{}WorkspaceControl".format(WORKSPACENAME)
DOCKTILE = "{} v{} -dockWidget".format(APPNAAME, VERS)
OBJECTNAME = "{}_mainWindow".format(APPNAAME)


def getIconPath():
    if not getattr(sys, "frozen", False):
        APP_ICONPATH = os.path.dirname(__file__).replace("\\", "/")
        return APP_ICONPATH
    else:
        # py2exe:
        APP_ICONPATH = "{}".format(os.path.dirname(sys.executable).replace("\\", "/"))
        return APP_ICONPATH


class Switch(QtWidgets.QMainWindow, IconMixin):
    themeChanged = QtCore.Signal(list, name="themeChanged")
    configChanged = QtCore.Signal(ss_configManager.Config, name="configChanged")
    _instance = None

    def __init__(self, themeName=None, themeColor=None, config=None, parent=None):
        """Creates the main ui layout for the app

        Args:
            config (Config):
            parent (QtWidget):
        """
        super(Switch, self).__init__(parent=parent)
        self._settings = QtCore.QSettings("JBD", "{}_settings".format(APPNAAME))
        self._recentConfigs = list()
        self._recentFilepaths = list()
        self._recentCustomBrowserPaths = list()
        self._customBrowserDockWidgets = list()
        self.config = config
        self.configPath = (
            os.path.join(self.config.projectPath(), self.config.projectName())
            if self.config
            else "No config found"
        )
        self.dw = None
        self.configDockWidget = None

        self.setWindowTitle("{} v{} : {}".format(APPNAAME, VERS, self.configPath))
        self.setObjectName(OBJECTNAME)
        self.setWindowIcon(
            QtGui.QIcon(
                QtCore.QDir(os.path.join(getIconPath(), "switchIcon.ico")).absolutePath()
            )
        )

        self.themeName = themeName if themeName is not None else "core"
        self.themeColor = themeColor if themeColor is not None else ""
        self.sheet = None
        self.setTheme(self.themeName, self.themeColor)

        self.mainMenuBar = QtWidgets.QMenuBar()
        self.mainMenuBar.setNativeMenuBar(True)
        self.setMenuBar(self.mainMenuBar)

        self.fileMenu = QtWidgets.QMenu("File", self)
        self.mainMenuBar.addMenu(self.fileMenu)

        # Menu Options
        self.loadConfig = self.fileMenu.addAction(
            self._fetchIcon("iconmonstr-login-icon-256"), "Load Project"
        )
        self.loadConfig.triggered.connect(self._loadConfig)

        self.createConfig = self.fileMenu.addAction(
            self._fetchIcon("iconmonstr-plus-1-240"), "Create / Update Schema Config"
        )
        self.createConfig.triggered.connect(self._createConfigUI)
        self.fileMenu.addSeparator()

        self.recentMenu = QtWidgets.QMenu("Recent Configs: ", self)
        self.fileMenu.addMenu(self.recentMenu)

        self.recentFilesMenu = QtWidgets.QMenu("Recent Files: ", self)
        self.fileMenu.addMenu(self.recentFilesMenu)

        self.addFileBrowser = self.fileMenu.addAction("Custom Browser")
        self.addFileBrowser.triggered.connect(self._addCustomBrowser)

        self.themeMenu = QtWidgets.QMenu("Theme", self)
        self.mainMenuBar.addMenu(self.themeMenu)
        self.toggleOnTopRB = self.themeMenu.addAction("onTop")
        self.toggleOnTopRB.setCheckable(True)
        self.toggleOnTopRB.toggled.connect(self._toggleOnTop)
        self.themeMenu.addSeparator()

        editMenu = self.themeMenu.addAction("Edit")
        editMenu.triggered.connect(self._editTheme)
        self.themeMenu.addSeparator()

        baseMenu = self.themeMenu.addAction("Dark")
        baseMenu.triggered.connect(partial(self.setTheme, self.themeName, ""))
        blueMenu = self.themeMenu.addAction("Blue")
        blueMenu.triggered.connect(partial(self.setTheme, self.themeName, "blue"))
        greenMenu = self.themeMenu.addAction("Green")
        greenMenu.triggered.connect(partial(self.setTheme, self.themeName, "green"))

        self.helpMenu = QtWidgets.QMenu("Help", self)
        self.mainMenuBar.addMenu(self.helpMenu)
        helpMenu = self.helpMenu.addAction("Overview")
        helpMenu.triggered.connect(self._showHelp)

        self.createFoldersButton = None
        # MAIN APP TOOLBAR
        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.setWindowTitle("mainToolBar")
        self.toolbar.setObjectName("mainToolBar")
        self.addToolBar(QtCore.Qt.LeftToolBarArea, self.toolbar)
        self._updateToolBarButtons()

        self.centerW = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(self.centerW)
        self._browserWidget = suiw_systemBrowser.SystemFileBrowser(
            config=self.config, themeName=self.themeName, themeColor=self.themeColor
        )
        layout.addWidget(self._browserWidget)
        self._browserWidget.fileOpened.connect(self._updateRecentFilesMenu)

        self.configChanged.connect(self._browserWidget.setConfig)
        self.themeChanged.connect(self._browserWidget.setTheme)
        self.setCentralWidget(self.centerW)

        self.resize(600, 800)

    def __new__(cls, themeName=None, themeColor=None, config=None, parent=None):
        if cls._instance is None:
            cls._instance = super(Switch, cls).__new__(cls)
            cls._instance.themeName = themeName
            cls._instance.themeColor = themeColor
            cls._instance.config = config
            cls._instance.parent = parent
        return cls._instance
    
    def _customBrowserWidgetExists(self, directoryPath):
        for widget in self._customBrowserDockWidgets:
            if widget.getDir() == directoryPath:
                return True
        return False

    def _customDockWidgetRemoved(self, dirPath):
        for widget in self._customBrowserDockWidgets:
            if widget.getDir() == dirPath:
                self._recentCustomBrowserPaths.remove(widget.getDir())
                self._customBrowserDockWidgets.remove(widget)

    def _addCustomBrowser(self, sender=None, dir=None):
        if dir is None:
            dir = QtWidgets.QFileDialog.getExistingDirectory(
                None,
                "Open Directory",
                "F:\\",
                QtWidgets.QFileDialog.ShowDirsOnly
                | QtWidgets.QFileDialog.DontResolveSymlinks,
            )
            if not dir:
                return

        if self._customBrowserWidgetExists(dir):
            return

        customBrowserWidget = CustomBrowserDockWidget(
            themeName=self.themeName, themeColor=self.themeColor, dir=dir
        )
        customBrowserWidget.closed.connect(self._customDockWidgetRemoved)
        self.themeChanged.connect(customBrowserWidget.setTheme)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, customBrowserWidget)
        self._customBrowserDockWidgets.append(customBrowserWidget)
        if dir not in self._recentCustomBrowserPaths:
            self._recentCustomBrowserPaths.append(dir)

    def _editTheme(self):
        self.editThemeUI = ThemeEditorDockWidget(
            themeName=self.themeName, themeColor=self.themeColor
        )
        self.editThemeUI.themeChanged.connect(self._themeEdited)
        self.editThemeUI.show()

    def _updateRecentFilesMenu(self, path=None):
        if path is not None and path not in self._recentFilepaths:
            self._recentFilepaths.append(path)

        self.recentFilesMenu.clear()
        for recentName in self._recentFilepaths[:10]:
            if not os.path.isfile(recentName):
                self._recentFilepaths.remove(recentName)
                logger.debug(
                    "Removed %s from recents as it no longer exists on disk.",
                    recentName,
                )
                continue

            act = self.recentFilesMenu.addAction(recentName)
            act.triggered.connect(partial(self._openFile, filepath=recentName))

    def _showHelp(self):
        self.helpUI = HelpView(self.themeName, self.themeColor)
        self.helpUI.show()

    def _updateToolBarButtons(self):
        self.toolbar.clear()
        if self.config is None:
            return

        self.toolbarLabel = QtWidgets.QLabel("Asset roots: ")
        self.toolbar.addWidget(self.toolbarLabel)

        rootList = list(self.config.iterRoots())
        rootList.sort()
        for rootDirName in ["root"] + rootList:
            self.toolbar.addSeparator()
            button = QtWidgets.QPushButton("..{}".format(rootDirName))
            button.clicked.connect(partial(self._changeRoot, rootDirName))
            self.toolbar.addWidget(button)

        self.toolbar.addSeparator()

        # Clear removes the create folders button so lets recreate that here instead..
        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding
        )
        self.toolbar.addWidget(spacer)

        createFoldersButton = QtWidgets.QPushButton(
            self._fetchIcon("iconmonstr-add-folder-icon-256"), "CreateFolders"
        )
        createFoldersButton.clicked.connect(self.createFolderUI)
        self.toolbar.addWidget(createFoldersButton)

    def _toggleOnTop(self, sender):
        if sender:
            self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(QtCore.Qt.Window)
        self.show(True)

    def _openFile(self, filepath):
        """Passes filepath along to the systemBrowser's file open.

        Args:
            filepath (string):
        """
        self._browserWidget._open(path=filepath, asFolder=False)

    def _loadConfig(self):
        self.configBrowser = suiw_configBrowser.ConfigBrowser(
            self.themeName, self.themeColor
        )
        self.configBrowser.show()
        self.configBrowser.fileSelected.connect(self.setConfig)

    def _createConfigUI(self):
        if self.configDockWidget is None:
            self.configDockWidget = ConfigDockWidget(self.themeName, self.themeColor)
            self.configDockWidget.setFloating(True)
            self.configDockWidget.resize(800, 600)
            self.themeChanged.connect(self.configDockWidget.setTheme)
            self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.configDockWidget)
        else:
            self.configDockWidget.show()

    def _changeRoot(self, dirName="root"):
        """Change the root dir of the treeView to be that of the clicked root button

        Args:
            dirName (string):
                One of the ss_folderManager.ROOTS
        """
        if dirName == "root":
            tokens = self.config.rootPathTokens()
        else:
            tokens = self.config.rootPathTokens() + [dirName]

        self._browserWidget.setprojectPath(tokens)

    def _createFolder(self, assetData):
        """Create the folders based off the widget's assetName and assetType

        Args:
            assetData (list[assetName, assetType]):
        """
        assetName, assetType = assetData
        ss_folderManager.createFolders(self.config, assetType, assetName)

    def createFolderUI(self):
        """Show the widget for creating a new folder"""
        if self.dw is None:
            self.dw = FolderDockWidget(
                self.themeName, self.themeColor, config=self.config
            )
            self.dw.commit.connect(self._createFolder)
            self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.dw)
            self.dw.resize(300, 300)
            self.resizeDocks([self.dw], [125], QtCore.Qt.Vertical)
        else:
            self.dw.show()

    def _themeEdited(self, edit):
        if edit:
            self.setTheme(self.themeName, self.themeColor)

    def setTheme(self, themeName, themeColor):
        """

        Args:
            themeName:
            themecolor:

        Returns:

        """
        self.sheet = st_factory.getThemeData(themeName, themeColor)
        self.themeName = themeName
        self.themeColor = themeColor
        self.setStyleSheet(self.sheet)
        self.themeChanged.emit([self.themeName, self.themeColor])

    def setConfig(self, filepath):
        """Sets a config for the application effectively swapping the application folders.

        Args:
            filepath (string): file path including extension to the json
        """
        if not filepath:
            return

        self.config = ss_configManager.getConfigByFilePath(filepath)
        self.config.setConfigPath(filepath)
        if self.config is not None and os.path.isfile(filepath):
            logger.debug("Setting config to: %s", filepath)
            if filepath not in self._recentConfigs:
                self._recentConfigs.append(filepath)
                act = self.recentMenu.addAction(filepath)
                act.triggered.connect(partial(self.setConfig, filepath=filepath))

        self.configPath = (
            self.config.projectPath() if self.config else "No config found"
        )
        self.setWindowTitle("{} v{} : {}".format(APPNAAME, VERS, self.configPath))
        self._updateToolBarButtons()

        # Close the createFolders wwidget.
        if self.dw is not None:
            self.dw.close()
            self.dw = None

        self.configChanged.emit(self.config)

    def closeEvent(self, e):
        self._settings.beginGroup("mainWindow")
        logger.debug("Saving windows settings now...")

        # Window size etc
        self._settings.setValue("recentConfigs", self._recentConfigs)
        self._settings.setValue("recentFilepaths", self._recentFilepaths)
        self._settings.setValue("themeName", self.themeName)
        self._settings.setValue("themeColor", self.themeColor)
        self._settings.setValue("recentCustomBrowsers", self._recentCustomBrowserPaths)

        if self.config is not None:
            self._settings.setValue("lastOpened", self.config.configPath())

        self._settings.setValue("geometry", self.saveGeometry())
        self._settings.setValue("state", self.saveState())

        self._settings.endGroup()
        # Force the show for the browsers settings to save
        self._browserWidget.close()
        super(Switch, self).closeEvent(e)

    def show(self, setOnTop=False):
        super(Switch, self).show()
        if setOnTop:
            return

        logger.debug("Applying windows settings now...")
        self._settings.beginGroup("mainWindow")

        # See Window Geometry for a discussion on why it is better to call QWidget::resize() and QWidget::move() rather
        # than QWidget::setGeometry() to restore a window's geometry.
        # self.resize(self._settings.value("size", defaultValue=QtCore.QSize(800, 600)))
        # self.move(self._settings.value("pos", defaultValue=QtCore.QPoint(0, 0)))

        self._recentConfigs = self._settings.value("recentConfigs", defaultValue=list())
        logger.debug("Restoring recentConfigs: %s", self._recentConfigs)
        for recentName in self._recentConfigs:
            if not os.path.isfile(recentName):
                self._recentConfigs.remove(recentName)
                logger.debug(
                    "Removed %s from recents as it no longer exists on disk.",
                    recentName,
                )
                continue

            act = self.recentMenu.addAction(recentName)
            act.triggered.connect(partial(self.setConfig, filepath=recentName))

        self._recentFilepaths = self._settings.value(
            "recentFilepaths", defaultValue=list()
        )
        logger.debug("Restoring recentConfigs: %s", self._recentConfigs)
        self._updateRecentFilesMenu()

        self.fileMenu.addSeparator()
        self.exitApp = self.fileMenu.addAction(
            self._fetchIcon("iconmonstr-x-mark-4-icon-256"), "Exit"
        )
        self.exitApp.triggered.connect(self.close)

        # Open the previous active config when the ui was closed.
        lastOpened = self._settings.value("lastOpened", defaultValue=None)
        logger.debug("lastOpened: %s", lastOpened)
        if lastOpened is not None and isinstance(lastOpened, str):
            logger.debug("Opening previous config: %s", lastOpened)
            if os.path.isfile(lastOpened):
                self.setConfig(lastOpened)

        # Theme restore
        themeName = self._settings.value("themeName", defaultValue="core")
        themeColor = self._settings.value("themeColor", defaultValue="")
        self.setTheme(themeName, themeColor)

        self._recentCustomBrowserPaths = list(
            set(self._settings.value("recentCustomBrowsers", defaultValue=[]))
        )
        for customBrowserPath in self._recentCustomBrowserPaths:
            self._addCustomBrowser(dir=customBrowserPath)

        self.restoreGeometry(self._settings.value("geometry"))
        self.restoreState(self._settings.value("state", QtCore.QByteArray()))

        self._settings.endGroup()
        # Force the show for the browsers settings to fire
        self._browserWidget.show()


if insideMaya:
    class MayaDockWidget(mag_mayaMixin.MayaQWidgetDockableMixin, QtWidgets.QWidget):
        def __init__(self, parent=None):
            super(MayaDockWidget, self).__init__(parent=parent)
            self.setObjectName(WORKSPACENAME)
            self.setWindowTitle(DOCKTILE)
            self.layout = QtWidgets.QVBoxLayout(self)


def getMayaDock():
    exists = cmds.workspaceControl(WORKSPACEDOCKNAME, q=True, exists=True)
    if not exists:
        dock = MayaDockWidget()
    else:
        docks = mag_mayaMixin.mixinWorkspaceControls
        for dockName, dock in docks.items():
            if dockName == WORKSPACEDOCKNAME:
                dock = dock
                break

    dock.show(dockable=True)
    return dock

def run(themeName=None, themeColor=None, filePath="", qtapp=None):
    """

    Args:
        themeName (string):
            name of the base theme in the themes folder
        themeColor (string):
            name of the color of the theme (if it exists) eg green, blue
        filePath (string):
            path to the config.json
        qtapp (QApplication):
            App for splashScr
    """

    config = ss_configManager.getConfigByFilePath(filePath)
    logger.debug("config: %s", config)

    app = Switch(themeName=themeName, themeColor=themeColor, config=config)
    if insideMaya:
        import shiboken2
        
        from maya.OpenMayaUI import MQtUtil as mqtutil
        ptr = mqtutil.findWindow(OBJECTNAME)
        # Find existing widget using mUtils .. cause singleton just refuses to work in maya regardless of approach
        dock = getMayaDock()
        if ptr:
            app = shiboken2.wrapInstance(int(ptr), QtWidgets.QWidget)
            dock.layout.addWidget(app)
        else:
            dock.layout.addWidget(app)
        dock.show()
        app.show()
    else:
        # Splash
        fp = QtCore.QDir(os.path.join(getIconPath(), "media", "splash.png"))
        logger.debug("fp: %s", fp.absolutePath())
        splashImage = QtGui.QPixmap()
        splashImage.load(fp.absolutePath())

        splashScr = SplashWidget(pixmap=splashImage)
        splashScr.resize(800, 200)
        splashScr.showMessage(
            "LOADING Switch Application...",
            alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom,
            color=QtCore.Qt.white,
        )
        splashScr.show()

        qtapp.processEvents()

        time.sleep(2.5)
        app.show()
        splashScr.finish(app)
    
    return app


if __name__ == "__main__":
    _settings = QtCore.QSettings("JBD", "{}_v{}".format(APPNAAME, VERS))
    _settings.beginGroup("mainWindow")
    lastOpened = _settings.value("lastOpened", defaultValue=None)
    _settings.endGroup()
    qtapp = QtWidgets.QApplication(sys.argv)
    logger.debug(
        "Starting {} v{} standalone...".format(
            qtapp.applicationName(), qtapp.applicationVersion()
        )
    )
    qtapp.setQuitOnLastWindowClosed(True)
    qtapp.setApplicationName(APPNAAME)
    qtapp.setApplicationVersion(VERS)
    qtapp.setOrganizationName("James B Dunlop")

    run(themeName=None, themeColor=None, filePath=lastOpened, qtapp=qtapp)
    sys.exit(qtapp.exec_())
