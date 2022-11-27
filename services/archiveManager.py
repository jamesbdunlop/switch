import os, sys
import logging
import zipfile

logger = logging.getLogger(__name__)


def archiveFile(inFilePath, outFilePath):
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
    if not os.path.isfile(inFilePath):
        logger.error("File path %s does not exist!", inFilePath)
        return False
    
    archive = zipfile.ZipFile(inFilePath)
    archive.extractall(path=rootDir)
    logger.info("Successfully restored %s to %s", inFilePath, rootDir)
    return True