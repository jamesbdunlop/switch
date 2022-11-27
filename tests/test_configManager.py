import os
import unittest


class Test_ConfigManager(unittest.TestCase):
    def setUp(self):
        self.curFolder = os.path.dirname(__file__)
        self.testConfigPath = os.path.join(self.curFolder, "testConfig.json")
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
