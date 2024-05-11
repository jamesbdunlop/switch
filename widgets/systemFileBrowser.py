import os, shutil
import logging
import shutil
from PySide6 import QtWidgets, QtCore, QtGui
from widgets.base import BaseTreeViewWidget
from services import archiveManager as ss_archiveManager
from functools import partial

insideMaya = False
try:
    from maya import cmds as cmds

    insideMaya = True
except ImportError:
    pass

logger = logging.getLogger(__name__)
logger.propagate = False
logging.basicConfig()


class Proxy(QtCore.QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def lessThan(self, left, right):
        leftData = self.sourceModel().data(left, QtCore.Qt.ItemDataRole.DisplayRole)
        rightData = self.sourceModel().data(right, QtCore.Qt.ItemDataRole.DisplayRole)
        left_tokens = leftData.split(" ")
        right_tokens = rightData.split(" ")
        # ['15/07/2022', '1:16', 'AM']
        if left_tokens[-1] in ("AM", "PM"):
            date_tokens = left_tokens[0].split("/")
            date = QtCore.QDate(
                int(date_tokens[-1]), int(date_tokens[1]), int(date_tokens[0])
            )
            time_tokens = left_tokens[1].split(":")
            time = QtCore.QTime(int(time_tokens[0]), int(time_tokens[1]), 0)
            dtLeft = QtCore.QDateTime(date, time)

            rdate_tokens = right_tokens[0].split("/")
            rdate = QtCore.QDate(
                int(rdate_tokens[-1]), int(rdate_tokens[1]), int(rdate_tokens[0])
            )
            rtime_tokens = right_tokens[1].split(":")
            rtime = QtCore.QTime(int(rtime_tokens[0]), int(rtime_tokens[1]), 0)
            dtRight = QtCore.QDateTime(rdate, rtime)
            return dtLeft < dtRight
        else:
            return QtCore.QSortFilterProxyModel.lessThan(self, left, right)


class SystemFileBrowser(BaseTreeViewWidget):
    fileOpened = QtCore.Signal(str, name="fileOpened")

    def __init__(self, config, themeName, themeColor, parent=None):
        super().__init__(themeName=themeName, themeColor=themeColor, parent=parent)
        self._settings = QtCore.QSettings("JBD", "switch_settings")
        self.config = config
        self.archiveFolderPath = None
        self._dir = QtCore.QDir()
        self._model = QtWidgets.QFileSystemModel()
        self.setSortingEnabled(True)

        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)

        # self._proxyModel = QtCore.QSortFilterProxyModel()
        self._proxyModel = Proxy()
        self._proxyModel.setSourceModel(self._model)
        self._proxyModel.setRecursiveFilteringEnabled(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ContiguousSelection)

        self.setModel(self._proxyModel)
        self.updateModelPath()

        # Fix the darn resize issues with the filebrowser
        for colIDX in range(self._proxyModel.sourceModel().columnCount()):
            self.header().setSectionResizeMode(
                colIDX, QtWidgets.QHeaderView.ResizeToContents
            )

        # Right click
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._rcMenu)

    def updateModelPath(self):
        # Init to the default project path
        if self.config is None:
            return

        rootPath = "/".join(self.config.rootPathTokens())
        logger.debug("rootPath: %s", rootPath)
        self._dir.setPath(rootPath)
        self._dir.makeAbsolute()
        if not self.createRootFolderPath(self._dir):
            return

        self.model().setRootPath(self._dir.path())
        idx = self.model().index(self._dir.path())
        self.setRootIndex(self._proxyModel.mapFromSource(idx))

    def createRootFolderPath(self, rootPath):
        """Checks if the folder exists on disk. Prompts to create if it doesn't returns bool if it exists for use or not.

        Args:
            rootPath (QDir):

        Returns:
            bool
        """
        if not os.path.exists(self._dir.path()):
            logger.warning("Root path does not exist!")
            confirm = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Warning,
                "Create?!",
                "Root project path doest not exist! Create it now?",
                QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel,
                None,
                QtCore.Qt.WindowStaysOnTopHint,
            )
            confirm.setStyleSheet(self.sheet)
            if confirm.exec_() == QtWidgets.QMessageBox.Ok:
                rootPath = rootPath.path()
                self._dir.mkpath(rootPath)
                for root in self.config.roots():
                    self._dir.mkpath(os.path.sep.join([rootPath, root]))
                return True

            return False

        return True

    def _rcMenu(self, point):
        self.menu = QtWidgets.QMenu()
        self.menu.setTitle("Actions:")
        self.menu.setWindowTitle("rcMenu")
        self.menu.setStyleSheet(self.sheet)
        if self._isDirectory():
            rootAction = self.menu.addAction(
                self._fetchIcon("iconmonstr-menu-4-240"), "Set As Root"
            )
            rootAction.triggered.connect(self._changeRootToSelected)

            openParentFolderAction = self.menu.addAction(
                self._fetchIcon("iconmonstr-login-icon-256"),
                "Explore to parent folder...",
            )
            openParentFolderAction.triggered.connect(self._openParentFolder)

            archiveDeleteAction = self.menu.addAction(
                self._fetchIcon("iconmonstr-zip-14-240"), "Archive +Del Folder"
            )
            archiveDeleteAction.triggered.connect(
                partial(self._archiveSelected, removeExisting=True)
            )

            archiveAction = self.menu.addAction(
                self._fetchIcon("iconmonstr-zip-14-240"), "Archive Folder"
            )
            archiveAction.triggered.connect(
                partial(self._archiveSelected, removeExisting=False)
            )

        if self._isValidFile():
            openAction = self.menu.addAction(
                self._fetchIcon("iconmonstr-shipping-box-10-icon-256"), "Open File"
            )
            openAction.triggered.connect(partial(self._open, asFolder=False))

            if insideMaya:
                importAction = self.menu.addAction(
                    self._fetchIcon("iconmonstr-upload-6-icon-256Yellow"), "Import File"
                )
                importAction.triggered.connect(self._importSelected)

        openCurrentFolderAction = self.menu.addAction(
            self._fetchIcon("iconmonstr-shipping-box-10-icon-256"),
            "Explore to folder...",
        )
        openCurrentFolderAction.triggered.connect(partial(self._open, asFolder=True))

        deleteAction = self.menu.addAction(
            self._fetchIcon("iconmonstr-trash-can-5-240"), "DELETE"
        )
        deleteAction.triggered.connect(self._deleteSelected)

        self.menu.move(self.mapToGlobal(point))
        self.menu.show()

    def _importSelected(self):
        rowIndices = self.selectedIndexes()
        srcIdx = self._proxyModel.mapToSource(rowIndices[0])
        path = self.model().filePath(srcIdx)
        cmds.file(path, i=True, f=True)

    def _openParentFolder(self):
        rowIndices = self.selectedIndexes()
        if not rowIndices:
            path = self.model().rootDirectory().absolutePath()
        else:
            srcIdx = self._proxyModel.mapToSource(rowIndices[0])
            path = self.model().filePath(srcIdx)

        if " " in path:
            logger.warning(
                "There are spaces in the path, remove the spaces if you wish to open this file!."
            )
            return

        parentPath = "/".join(path.split("/")[:-1])
        service = QtGui.QDesktopServices()
        service.openUrl(QtCore.QUrl(parentPath))

    def _open(self, sender=None, path=None, asFolder=False):
        if path is None:
            rowIndices = self.selectedIndexes()
            if not rowIndices:
                path = self.model().rootDirectory().absolutePath()
            else:
                srcIdx = self._proxyModel.mapToSource(rowIndices[0])
                path = self.model().filePath(srcIdx)

        if " " in path:
            logger.warning(
                "There are spaces in the path, remove the spaces if you wish to open this file!."
            )
            return

        if asFolder:
            if not os.path.isdir(path):
                path = os.path.dirname(path)
            logger.debug("System: opening %s", path)
            service = QtGui.QDesktopServices()
            service.openUrl(QtCore.QUrl(path))
            return

        if insideMaya:
            logger.debug("Maya: opening %s", path)
            cmds.file(path, o=True, f=True)
        else:
            logger.debug("System: opening %s", path)
            service = QtGui.QDesktopServices()
            service.openUrl(QtCore.QUrl(path))

    def _isDirectory(self):
        rowIndices = self.selectedIndexes()
        if not rowIndices:
            path = self.model().rootDirectory().absolutePath()
        else:
            srcIdx = self._proxyModel.mapToSource(rowIndices[0])
            path = self.model().filePath(srcIdx)

        if os.path.isdir(path):
            return True

        return False

    def _isValidFile(self, path=None):
        if path is None:
            rowIndices = self.selectedIndexes()

            if not rowIndices:
                path = self.model().rootDirectory().absolutePath()
            else:
                srcIdx = self._proxyModel.mapToSource(rowIndices[0])
                path = self.model().filePath(srcIdx)

        valid = self.config.validExtensions()
        if os.path.isfile(path):
            _, ext = os.path.splitext(path)
            if ext in valid:
                return True

        return False

    def _changeRootToSelected(self):
        rowIndices = self.selectedIndexes()
        if not rowIndices:
            return

        srcIdx = self._proxyModel.mapToSource(rowIndices[0])
        dirPath = self.model().filePath(srcIdx)
        if os.path.isfile(dirPath):
            return

        self.setprojectPath(dirPath.split("/"))

    def _collapseHrc(self, qmodelIndex):
        """Method to collapse all children on shift+click

        Args:
            qmodelIndex (QtCore.QModelIndex):
        """
        if self._proxyModel.hasChildren(qmodelIndex):
            rowCount = self._proxyModel.rowCount(qmodelIndex)
            for idx in range(rowCount):
                child = qmodelIndex.child(idx, 0)
                self.collapse(child)

    def _deleteSelected(self):
        confirm = QtWidgets.QMessageBox(
            QtWidgets.QMessageBox.Warning,
            "Delete?!",
            "Are you sure?",
            QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel,
            None,
            QtCore.Qt.WindowStaysOnTopHint,
        )
        confirm.setStyleSheet(self.sheet)
        if confirm.exec_() != QtWidgets.QMessageBox.Ok:
            return
        rowIndices = self.selectedIndexes()
        for row in rowIndices:
            srcIdx = self._proxyModel.mapToSource(row)
            if srcIdx.column() != 0:
                continue

            path = self.model().filePath(srcIdx)
            if os.path.isfile(path):
                os.remove(path)
                logger.debug("Successfully removed file!")
            elif os.path.isdir(path):
                shutil.rmtree(path)
                logger.debug("Successfully removed directory!")

    def _archiveSelected(self, removeExisting=False):
        """_summary_

        Args:
            removeExisting (bool, optional): _description_. Defaults to False.
        """
        # Warn user first
        if removeExisting:
            title = "Archive And Delete?!"
            msg = "Using this action will zip and delete the selected folders."
        else:
            title = "Archive?!"
            msg = "Using this action will zip the selected folders."

        confirm = QtWidgets.QMessageBox(
            QtWidgets.QMessageBox.Warning,
            title,
            msg,
            QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel,
            None,
            QtCore.Qt.WindowStaysOnTopHint,
        )
        confirm.setStyleSheet(self.sheet)
        if confirm.exec_() != QtWidgets.QMessageBox.Ok:
            return

        # Check for previously archived to path. Prompt user to use this or not.
        usePrevious = False
        if self.archiveFolderPath is not None:
            confirm2 = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Warning,
                "Use Previous Archive Folder?",
                "Archive to: {}".format(self.archiveFolderPath),
                QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.No,
                None,
                QtCore.Qt.WindowStaysOnTopHint,
            )
            confirm2.setStyleSheet(self.sheet)
            if confirm2.exec_() == QtWidgets.QMessageBox.Ok:
                usePrevious = True

        if not usePrevious:
            dir = QtWidgets.QFileDialog.getExistingDirectory(
                None,
                "Open Directory",
                self.archiveFolderPath,
                QtWidgets.QFileDialog.ShowDirsOnly
                | QtWidgets.QFileDialog.DontResolveSymlinks,
            )
            if not dir:
                return
            self.archiveFolderPath = dir
        else:
            dir = self.archiveFolderPath

        rowIndices = self.selectedIndexes()
        for row in rowIndices:
            srcIdx = self._proxyModel.mapToSource(row)
            if srcIdx.column() != 0:
                continue
            path = self.model().filePath(srcIdx)
            if os.path.isdir(path):
                # TODO : check this over for a more generic approach
                zippath = "{}\\{}_{}_{}_{}.zip".format(
                    dir,
                    path.split("/")[-4],
                    path.split("/")[-3],
                    path.split("/")[-2],
                    path.split("/")[-1],
                )
                logger.info("Archiving and cleaning: %s to %s", path, zippath)
                result = ss_archiveManager.archiveFolder(
                    inDirPath=path, outFilePath=zippath
                )
                if not result:
                    continue

                if removeExisting:
                    shutil.rmtree(path)

    def dragMoveEvent(self, event) -> None:
        super(SystemFileBrowser, self).dragMoveEvent(event)
        # print("dragMoveEvent: %s", event.mimeData().urls())
        pos = event.pos()
        idx = self.indexAt(pos)
        srcIdx = self._proxyModel.mapToSource(idx)
        path = self.model().filePath(srcIdx)
        if os.path.isdir(path):
            return event.accept()

    def dragEnterEvent(self, event) -> None:
        super(SystemFileBrowser, self).dragEnterEvent(event)
        for url in event.mimeData().urls():
            # print(event.proposedAction()) # PySide2.QtCore.Qt.DropAction.MoveAction
            filePath = url.toLocalFile()
            if not os.path.isfile(filePath):
                # We don't allow moving folders.
                return event.ignore()

        return event.accept()

    def dropEvent(self, event) -> None:
        super(SystemFileBrowser, self).dropEvent(event)
        # drop location
        pos = event.pos()
        idx = self.indexAt(pos)
        srcIdx = self._proxyModel.mapToSource(idx)
        destPath = self.model().filePath(srcIdx)

        for url in event.mimeData().urls():
            srcPath = url.toLocalFile()
            fileName = srcPath.split("/")[-1]
            if event.keyboardModifiers() == QtCore.Qt.ControlModifier:
                shutil.copy2(srcPath, os.path.sep.join([destPath, fileName]))
            else:
                shutil.move(srcPath, os.path.sep.join([destPath, fileName]))

    def model(self):
        """Returns the QFileSystemModel from the proxyModel"""
        return self._proxyModel.sourceModel()

    def setprojectPath(self, tokens):
        """Set a new projectPath for the viewer

        Args:
            tokens (list["drive", "dir01", "dir02"..]):
        """
        path = "/".join(tokens)
        self._dir.setPath(path)
        self._dir.makeAbsolute()
        if not os.path.isdir(self._dir.path()):
            confirm = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Warning,
                "Create?!",
                "This root path doest not exist! Create it now?",
                QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel,
                None,
                QtCore.Qt.WindowStaysOnTopHint,
            )
            confirm.setStyleSheet(self.sheet)
            if confirm.exec_() == QtWidgets.QMessageBox.Ok:
                self._dir.mkpath(self._dir.path())

        self._proxyModel.sourceModel().setRootPath(self._dir.path())
        idx = self._proxyModel.sourceModel().index(self._dir.path())
        self.setRootIndex(self._proxyModel.mapFromSource(idx))
        # self.setRootIndex(self._proxyModel.sourceModel().index(self._dir.path()))
        logger.debug("Changed path to: %s", self._dir.path())

        try:
            # Maya's workspace
            cmds.workspace(directory=self._dir.path())
            logger.debug("Workspace changed to: %s", self._dir.path())
        except NameError:
            pass

    def mouseDoubleClickEvent(self, e):
        """Overload the mouseDoubleClick for checking filepaths"""
        super(SystemFileBrowser, self).mouseDoubleClickEvent(e)
        modelIdx = self.indexAt(e.pos())
        srcIdx = self._proxyModel.mapToSource(modelIdx)
        path = self.model().filePath(srcIdx)
        if self._isValidFile(path):
            logger.debug("Opening %s", path)
            if insideMaya:
                cmds.file(path, o=True, f=True)
            else:
                self._open(path)

            self.fileOpened.emit(path)

    def mousePressEvent(self, e):
        """Overload the mousePressEvent for keyboard mods"""
        super(SystemFileBrowser, self).mousePressEvent(e)
        keyboardMod = e.modifiers()
        modelIdx = self.indexAt(e.pos())

        if keyboardMod == QtCore.Qt.ControlModifier:
            self.expandRecursively(modelIdx, -1)

        if keyboardMod == QtCore.Qt.ShiftModifier:
            self._collapseHrc(qmodelIndex=modelIdx)

    def setConfig(self, config):
        """Change the config being used by the fileSystem.

        Args:
            config (Config):
        """
        self.config = config
        self.updateModelPath()

    def closeEvent(self, e):
        self._settings.beginGroup("sysBrowserWindow")
        self._settings.setValue("archiveFolderPath", self.archiveFolderPath)
        self._settings.endGroup()
        super(SystemFileBrowser, self).closeEvent(e)

    def show(self, setOnTop=False):
        super(SystemFileBrowser, self).show()
        self._settings.beginGroup("sysBrowserWindow")
        self.archiveFolderPath = self._settings.value(
            "archiveFolderPath", defaultValue=""
        )
        self._settings.endGroup()


class CustomFileBrowser(BaseTreeViewWidget):
    def __init__(self, rootDir, themeName, themeColor, parent=None):
        super().__init__(themeName=themeName, themeColor=themeColor, parent=parent)
        self._dir = QtCore.QDir()
        self._model = QtWidgets.QFileSystemModel()
        self.setSortingEnabled(True)

        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)

        # self._proxyModel = QtCore.QSortFilterProxyModel()
        self._proxyModel = Proxy()
        self._proxyModel.setSourceModel(self._model)
        self._proxyModel.setRecursiveFilteringEnabled(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ContiguousSelection)

        self.setModel(self._proxyModel)

        # Fix the darn resize issues with the filebrowser
        for colIDX in range(self._proxyModel.sourceModel().columnCount()):
            self.header().setSectionResizeMode(
                colIDX, QtWidgets.QHeaderView.ResizeToContents
            )

        self._dir.setPath(rootDir)
        self._dir.makeAbsolute()
        self.model().setRootPath(self._dir.path())
        idx = self.model().index(self._dir.path())
        self.setRootIndex(self._proxyModel.mapFromSource(idx))

        # Right click
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._rcMenu)

    def selHasArchive(self):
        rowIndices = self.selectedIndexes()
        for row in rowIndices:
            srcIdx = self._proxyModel.mapToSource(row)
            if srcIdx.column() != 0:
                continue

            path = self.model().filePath(srcIdx)
            if os.path.isfile(path) and path.endswith(".zip"):
                return True
        return False

    def _rcMenu(self, point):
        rowIndices = self.selectedIndexes()
        if not rowIndices:
            return

        self.menu = QtWidgets.QMenu()
        self.menu.setTitle("Actions:")
        self.menu.setWindowTitle("rcMenu")
        self.menu.setStyleSheet(self.sheet)

        deleteAction = self.menu.addAction(
            self._fetchIcon("iconmonstr-trash-can-5-240"), "DELETE"
        )
        deleteAction.triggered.connect(self._deleteSelected)

        if self.selHasArchive():
            restoreArchiveAction = self.menu.addAction(
                self._fetchIcon("iconmonstr-zip-14-240"), "Restore Archive"
            )
            restoreArchiveAction.triggered.connect(self._restoreArchive)

        self.menu.move(self.mapToGlobal(point))
        self.menu.show()

    def _open(self, sender=None, path=None, asFolder=False):
        if path is None:
            rowIndices = self.selectedIndexes()
            if not rowIndices:
                path = self.model().rootDirectory().absolutePath()
            else:
                srcIdx = self._proxyModel.mapToSource(rowIndices[0])
                path = self.model().filePath(srcIdx)

        if " " in path:
            logger.warning(
                "There are spaces in the path, remove the spaces if you wish to open this file!."
            )
            return

        logger.debug("System: opening %s", path)
        service = QtGui.QDesktopServices()
        service.openUrl(QtCore.QUrl(path))

    def _isValidFile(self, path=None):
        if path is None:
            rowIndices = self.selectedIndexes()

            if not rowIndices:
                path = self.model().rootDirectory().absolutePath()
            else:
                srcIdx = self._proxyModel.mapToSource(rowIndices[0])
                path = self.model().filePath(srcIdx)

        return os.path.isfile(path)

    def _restoreArchive(self):
        confirm = QtWidgets.QMessageBox(
            QtWidgets.QMessageBox.Warning,
            "Restore Archive?!",
            "Are you sure?",
            QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel,
            None,
            QtCore.Qt.WindowStaysOnTopHint,
        )
        confirm.setStyleSheet(self.sheet)
        if confirm.exec_() != QtWidgets.QMessageBox.Ok:
            return

        rootDir = QtWidgets.QFileDialog.getExistingDirectory(
            None,
            "Root Directory",
            "",
            QtWidgets.QFileDialog.ShowDirsOnly
            | QtWidgets.QFileDialog.DontResolveSymlinks,
        )
        if not dir:
            rootDir

        rowIndices = self.selectedIndexes()
        for row in rowIndices:
            srcIdx = self._proxyModel.mapToSource(row)
            if srcIdx.column() != 0:
                continue

            path = self.model().filePath(srcIdx)
            if os.path.isfile(path) and path.endswith(".zip"):
                logger.info("Restoring archive: %s", path)
                ss_archiveManager.restoreFile(path, rootDir)
            else:
                logger.info("Can not restore: %s not a valid .zip archive!", path)

    def _deleteSelected(self):
        confirm = QtWidgets.QMessageBox(
            QtWidgets.QMessageBox.Warning,
            "Delete?!",
            "Are you sure?",
            QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel,
            None,
            QtCore.Qt.WindowStaysOnTopHint,
        )
        confirm.setStyleSheet(self.sheet)
        if confirm.exec_() != QtWidgets.QMessageBox.Ok:
            return

        rowIndices = self.selectedIndexes()
        for row in rowIndices:
            srcIdx = self._proxyModel.mapToSource(row)
            if srcIdx.column() != 0:
                continue

            path = self.model().filePath(srcIdx)
            if os.path.isfile(path):
                os.remove(path)
                logger.debug("Successfully removed file!")
            elif os.path.isdir(path):
                shutil.rmtree(path)
                logger.debug("Successfully removed directory!")

    def model(self):
        """Returns the QFileSystemModel from the proxyModel"""
        return self._proxyModel.sourceModel()

    def dragMoveEvent(self, event) -> None:
        super(CustomFileBrowser, self).dragMoveEvent(event)
        pos = event.pos()
        idx = self.indexAt(pos)
        srcIdx = self._proxyModel.mapToSource(idx)
        path = self.model().filePath(srcIdx)
        logger.debug("path: %s", path)
        if not path:
            path = self._dir.path()

        if os.path.isdir(path):
            return event.accept()

    def dragEnterEvent(self, event) -> None:
        super(CustomFileBrowser, self).dragEnterEvent(event)
        for url in event.mimeData().urls():
            filePath = url.toLocalFile()
            logger.debug("filepath: %s", filePath)
            if not os.path.isfile(filePath):
                # We don't allow moving folders.
                return event.ignore()

        return event.accept()

    def dropEvent(self, event) -> None:
        super(CustomFileBrowser, self).dropEvent(event)
        # drop location
        pos = event.pos()
        idx = self.indexAt(pos)
        srcIdx = self._proxyModel.mapToSource(idx)
        destPath = self.model().filePath(srcIdx)
        if not destPath:
            destPath = self._dir.path()
            logger.info("No valid drop path found, setting to root: %s", destPath)

        for url in event.mimeData().urls():
            srcPath = url.toLocalFile()
            fileName = srcPath.split("/")[-1]
            if event.keyboardModifiers() == QtCore.Qt.ControlModifier:
                shutil.copy2(srcPath, os.path.sep.join([destPath, fileName]))
            else:
                shutil.move(srcPath, os.path.sep.join([destPath, fileName]))

    def model(self):
        """Returns the QFileSystemModel from the proxyModel"""
        return self._proxyModel.sourceModel()

    def mouseDoubleClickEvent(self, e):
        """Overload the mouseDoubleClick for checking filepaths"""
        super(CustomFileBrowser, self).mouseDoubleClickEvent(e)
        modelIdx = self.indexAt(e.pos())
        srcIdx = self._proxyModel.mapToSource(modelIdx)
        path = self.model().filePath(srcIdx)
        if self._isValidFile(path):
            logger.debug("Opening %s", path)
            self._open(path)

    def mousePressEvent(self, e):
        """Overload the mousePressEvent for keyboard mods"""
        super(CustomFileBrowser, self).mousePressEvent(e)
        keyboardMod = e.modifiers()
        modelIdx = self.indexAt(e.pos())
