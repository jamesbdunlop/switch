import os
import unittest
from services import archiveManager as ss_archiveManager


class Test_ArchiveManager(unittest.TestCase):
    def setUp(self):
        self.rootDir = "C:\\"
        self.tempDir = "temp"
        self.tempDirPath = os.path.join(self.rootDir, self.tempDir)
        self.curFolder = os.path.dirname(__file__)
        self.testTxtFilePath = os.path.join(self.curFolder, "toarchive.txt")
        self.destZipPath = os.path.join(self.tempDirPath, "testZipFile.zip")
        return super().setUp()

    def tearDown(self) -> None:
        if os.path.isfile(self.destZipPath):
            os.remove(self.destZipPath)
        return super().tearDown()

    def test_tmpDirExists(self):
        self.assertTrue(os.path.isdir(self.tempDirPath))

    def test_archiveFile(self):
        val = ss_archiveManager.archiveFile(
            inFilePath=self.testTxtFilePath, outFilePath=self.destZipPath
        )
        self.assertTrue(val)
        self.assertTrue(os.path.isfile(self.destZipPath))

    def test_archiveFolder(self):
        val = ss_archiveManager.archiveFolder(
            inDirPath=self.curFolder, outFilePath=self.destZipPath
        )
        self.assertTrue(val)
        self.assertTrue(os.path.isfile(self.destZipPath))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
