import os
import logging
from PySide2 import QtCore

logger = logging.getLogger(__name__)
logger.propagate = False
logging.basicConfig()


def _getBaseFolderPath(config):
    """Combine the root folders into a string

    Args:
        config (Config):

    Returns:
        str
    """
    projectPath = config.projectPath()
    tokens = projectPath.split("/")
    base = os.path.sep.join(tokens)
    return base


def _createFolders(pathTo, folderData):
    """Used recursively through the folderData to create all the schema's folders.

    Args:
        pathTo (str):
        folderData (dict):
    """
    for folderName, subFolders in folderData.items():
        folderPath = os.path.sep.join([pathTo, folderName])
        if not os.path.isdir(folderPath):
            qdir = QtCore.QDir()
            qdir.mkpath(folderPath)

        if subFolders is None:
            continue

        _createFolders(folderPath, subFolders)


def createFolders(config, assetType, assetName):
    """

    Args:
        config (Config):
            The show config for folder schema's etc
        assetType (str):
            The name of the assetType folder.For a valid list check the Config class eg: CHAR PROP etc
        assetName (str):
            The name of the asset
    """
    baseFolderPath = _getBaseFolderPath(config)
    folderPath = os.path.sep.join([baseFolderPath, config.configRoot(), assetType, assetName])
    logger.debug("Creating folders for assetType: %s | assetName: %s", assetType, assetName)
    logger.debug("baseFolderPath: %s", baseFolderPath)
    logger.debug("folderPath: %s", folderPath)
    if not os.path.isdir(folderPath):
        qdir = QtCore.QDir()
        qdir.setPath(folderPath)
        qdir.makeAbsolute()
        qdir.mkpath(folderPath)
        logger.debug("Created %s ", qdir.path())

    _createFolders(folderPath, config.baseFolders())
