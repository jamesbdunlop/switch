import os, sys
import logging
from dataclasses import dataclass
from constants import schema as   c_schema
from PySide2 import QtCore
import json

logger = logging.getLogger(__name__)
logger.propagate = False
logging.basicConfig()


@dataclass
class Config:
    """
    Note class and it's methods directly relate to the setup I was using
    PROJPATH|projectName|configRoot|ROOTS|assetName|BASEFOLDERS|ASSETFOLDERS|publish|PUBLISHFOLDERS
                                                                    |reference|REFFOLDERS
                                                                    |review|
                                                                    |work|WORKFOLDERS|images
                                                                                     |maya|MAYAFOLDERS
                                                                                     |zbrush|ZBRUSHFOLDERS

    When definiing your own you should look to make sure your config.json has keys
    "configRoot": [rootFoldername eg: assets, sequences etc]
    "ROOTS": {}
    "BASEFOLDERS": {}
    From there you are free to add any named kind of folderSchema  you want.
    """

    data: dict
    _configName = str
    _configPath = str

    def name(self):
        """Returns name of the config being used

        Returns (string):
        """
        return self._configName

    def setName(self, confgName):
        self._configName = confgName

    def projectName(self):
        return self.data.get("projectName", "")

    def projectPath(self):
        return self.data.get("projectPath", "")

    def configPath(self):
        return self._configPath

    def setConfigPath(self, filePath):
        """

        Args:
            filePath (string):
        """
        self._configPath = filePath

    def projectPathTokens(self):
        return self.data.get("projectPath", "").split("/")

    def configRoot(self):
        return self.data.get("configRoot", "")

    def rootPathTokens(self):
        return self.projectPathTokens() + [self.projectName(), self.configRoot()]

    def validExtensions(self):
        return self.data.get(
            "validExt",
            (
                ".ma",
                ".mb",
                ".obj",
                ".jpg",
                ".png",
                ".ZPR",
                ".tif",
                ".tga",
                ".zpr",
                ".stl",
                ".ZTL",
                ".lys",
                ".dlp",
            ),
        )

    def iterBaseFolders(self):
        data = self.data.get("BASEFOLDERS", {})
        for folderName, linkedData in data.items():
            if not linkedData:
                linkedData = str(None)
            if not isinstance(linkedData, list):
                linkedData = [linkedData]
            yield folderName, linkedData

    def getLinkedSubFolder(self, name):
        """Get a specific linked folder's value (dict)"""
        return self.data.get(name, {})
        
    def iterLinkedSubFolderData(self, data):
        for subFolderName, folders in data.items():
            if not isinstance(folders, list):
                folders = [folders]
            
            yield subFolderName, folders

    def linkedFolderNames(self):
        """ Return a list of all the linked folder entries """
        invalidKeys = c_schema.IGNORES_LINKED
        names = []
        for k, _ in self.data.items():
            if k in invalidKeys:
                continue
            names.append(k)
            
        return names

    def roots(self):
        return self.data.get("ROOTS", {})

    def parseRoots(self):
        return self._parseData(self.data.get("ROOTS", {}))
    
    def parseBaseFolders(self):
        return self._parseData(self.data.get("BASEFOLDERS", {}))
    
    def iterRoots(self):
        """Generator to iter the roots entry in the dict.

        Yields:
            list
        """
        for root in self.data.get("ROOTS", {}).keys():
            yield root

    def _parseData(self, data):
        """Mutates data to fill in anything that expects to reuse other key values.

        Args:
            data (dict):

        Returns:
            dict
        """
        for folderName, folderData in data.items():
            logger.debug("folderName: %s folderData: %s", folderName, folderData)
            if folderName in ("projectName", "projectPath", "configRoot"):
                logger.debug("Skipping %s %s", folderName, folderData)
                continue

            # None, String, Dict
            if folderData is None or folderData == "None":
                logger.debug("Skipping %s %s", folderName, folderData)
                continue

            if isinstance(folderData, str):
                logger.debug("Found subFolder name...")
                d = self.data.get(folderData)
                data[folderName] = self._parseData(d)

        return data
    
def getConfigByFilePath(filepath):
    """

    Args:
        filepath (string):

    Returns:
        Config
    """
    if filepath is None:
        return

    if not filepath.endswith(".json"):
        filepath = "{}.json".format(filepath)

    qdir = QtCore.QDir()
    qdir.setPath(filepath)
    qdir.makeAbsolute()
    logger.debug("Fetching config: %s", qdir.path())
    configPath = qdir.path()
    if not os.path.isfile(configPath):
        logger.warning("Config does not exist! \n\t%s", configPath)
        return

    data = loadJson(configPath)
    config = Config(data=data)
    config.setName(getConfigNameFromFilePath(filepath))

    return config


def getConfigFilepath(configName):
    """

    Args:
        configName (string):

    Returns:
        string
    """
    if not configName:
        return None

    if not getattr(sys, "frozen", False):
        currentPath = os.path.dirname(__file__).replace("\\", "/")
    else:
        currentPath = os.path.dirname(sys.executable).replace("\\", "/")

    tokens = os.path.split(currentPath)
    currentPath = os.path.sep.join(tokens[:-1])
    configPath = "{}.json".format(
        os.path.sep.join([currentPath, "configs", configName])
    )
    qdir = QtCore.QDir()
    qdir.setPath(configPath)
    qdir.makeAbsolute()
    logger.debug("Fetching config: %s", qdir.path())
    configPath = qdir.path()
    if not os.path.isfile(configPath):
        logger.warning("Config does not exist! \n\t%s", configPath)
        return None

    return qdir.path()


def getConfigNameFromFilePath(filepath):
    """

    Args:
        filepath (string):

    Returns:
        string
    """
    tokens = os.path.split(filepath)
    fileName = tokens[-1].split(".")[0]
    logger.debug("fileName: %s", fileName)
    return fileName


def getConfigByName(configName):
    """

    Args:
        configName (string):

    Returns:
        Config
    """

    configPath = getConfigFilepath(configName)
    data = loadJson(configPath)
    config = Config(data=data)
    config.setName(configName)
    return config


def loadJson(filepath):
    """

    Args:
        filepath (string):

    Returns:
        dict
    """
    logger.debug("filepath: %s", filepath)
    if filepath is None:
        return {}

    if not os.path.isfile(filepath):
        return {}

    with open(filepath) as infile:
        data = json.load(infile)

    return data


def saveConfig(filepath, data):
    """Save the json file using the configName and the dict()

    Args:
        filepath (string):
        data (dict):
    """
    if not filepath:
        return None

    if not filepath.endswith(".json"):
        filepath = "{}.json".format(filepath)

    logger.debug("Saving config: %s", filepath)
    with open(filepath, "w") as outfile:
        outfile.write(json.dumps(data))
