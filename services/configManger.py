import os, sys
import logging
from dataclasses import dataclass
from PySide2 import QtCore
import simplejson as sjson

logger = logging.getLogger(__name__)
logger.propagate = False
logging.basicConfig()

frozen = getattr(sys, 'frozen', '')


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

    def name(self):
        return self._configName

    def setName(self, confgName):
        self._configName = confgName

    def baseFolders(self):
        return self._parseData(self.data.get("BASEFOLDERS", {}))

    def roots(self):
        return self._parseData(self.data.get("ROOTS", {}))

    def rootsAslist(self):
        """

        Returns:
            list
        """
        roots = [root for root in self.data.get("ROOTS", {}).keys()]
        return roots

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
        return self.projectPathTokens() + [self.configRoot()]


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

    if not frozen:
        currentPath = os.path.dirname(__file__).replace("\\", "/")
    elif frozen in ('dll', 'console_exe', 'windows_exe'):
        # py2exe:
        currentPath = os.path.dirname(sys.executable).replace("\\", "/")

    tokens = os.path.split(currentPath)
    currentPath = os.path.sep.join(tokens[:-1])
    configPath = "{}.json".format(os.path.sep.join([currentPath, "configs", configName]))
    qdir = QtCore.QDir()
    qdir.setPath(configPath)
    qdir.makeAbsolute()
    logger.debug("Fetching config: %s", qdir.path())
    configPath = qdir.path()
    if not os.path.isfile(configPath):
        logger.warning("Config does not exist! \n\t%s",configPath)
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
        data = sjson.load(infile)

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
        outfile.write(sjson.dumps(data))

