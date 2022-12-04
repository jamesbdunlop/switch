import os, sys
import logging
import zipfile

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
        logger.error("File path %s does not exist!", inFilePath)
        return False

    if os.path.isfile(outFilePath):
        logger.error("%s already exists!", outFilePath)
        return

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
        logger.error("Directory path %s does not exist!", inDirPath)
        return False

    if os.path.isfile(outFilePath):
        logger.error("%s already exists!", outFilePath)
        return

    with zipfile.ZipFile(outFilePath, "w") as myzip:
        for root, dirs, files in os.walk(inDirPath, topdown=True):
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
        logger.error("File path %s does not exist!", inFilePath)
        return False
    
    archive = zipfile.ZipFile(inFilePath)
    archive.extractall(path=rootDir)
    logger.info("Successfully restored %s to %s", inFilePath, rootDir)
    return True


if __name__ == "__main__":
    path = "C:\\_recovery\\baseconfig_assets_Character_Arachne.zip"
    restoreFile(inFilePath=path, rootDir="C:\\temp")