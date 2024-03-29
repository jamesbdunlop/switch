import os, sys
import logging
import zipfile
import widgets.utils as widgetUtils

logger = logging.getLogger(__name__)


def archiveFile(inFilePath, outFilePath):
    """Archive a file to zip.

    Args:
        inFilePath (str): full file path including ext of the file to archive.
        outFilePath (str): full file path including ext to archive to.

    Returns:
        bool: success or fail
    """
    if not os.path.isfile(inFilePath):
        message = "File path %s is not a file!", inFilePath
        widgetUtils.errorWidget(title="File path error.", message=message)
        return False

    if os.path.isfile(outFilePath):
        message = "%s already exists!", outFilePath
        widgetUtils.errorWidget(title="File already exists.", message=message)
        return False

    with zipfile.ZipFile(outFilePath, "w") as myzip:
        myzip.write(inFilePath)

    return True


def archiveFolder(inDirPath, outFilePath):
    """Archive a folder to zip.

    Args:
        inDirPath (str): full dir path of the dir to archive.
        outFilePath (str): full zip path to archive to.

    Returns:
        bool: success or fail
    """
    if not os.path.isdir(inDirPath):
        logger.info("Directory path %s does not exist!", inDirPath)
        return False

    if os.path.isfile(outFilePath):
        message = "Can not archive this file as file already exists on disk. \nPlease remove existing an try again."
        widgetUtils.errorWidget(title="File exists.", message=message)
        return False

    with zipfile.ZipFile(outFilePath, "w") as myzip:
        for root, _, files in os.walk(inDirPath, topdown=True):
            for file in files:
                fp = os.path.join(root, file)
                myzip.write(fp)

    return True


def restoreFile(inFilePath, rootDir):
    """From an archive filepath restore to a directory.

    Args:
        inFilePath (str): full file path including ext of the file to archive.
        rootDir (str): full dir path to archive to.

    Returns:
        bool: success for fail
    """
    if not os.path.isfile(inFilePath):
        message = "Can not restore archive as it does not exist on disk!?"
        widgetUtils.errorWidget(title="Filepath does not exist.", message=message)
        return False

    archive = zipfile.ZipFile(inFilePath)
    archive.extractall(path=rootDir)
    logger.info("Successfully restored %s to %s", inFilePath, rootDir)
    return True


if __name__ == "__main__":
    path = "C:\\_recovery\\baseconfig_assets_Character_Arachne.zip"
    restoreFile(inFilePath=path, rootDir="C:\\temp")
