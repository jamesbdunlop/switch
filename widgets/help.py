import sys
import logging
from PySide2 import QtWidgets, QtCore
from widgets.base import BaseWidget as BaseWidget

logger = logging.getLogger(__name__)
logger.propagate = False
logging.basicConfig()


class HelpView(BaseWidget):
    def __init__(self, themeName, themeColor, parent=None):
        BaseWidget.__init__(self, themeName=themeName, themeColor=themeColor, parent=parent)

        self.setWindowTitle("Help:")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self._mainLayout = QtWidgets.QVBoxLayout(self)
        htmlStr = "<body>" \
                  "<h1>Overview:</h1>" \
                  "<br>Switch is a small tool to help create configs for folder schema's that you can use to navigate" \
                  " and create folders for home projects. eg:" \
                  "<br><pre>PROJPATH|projectName|configRoot|ROOTS|assetName|BASEFOLDERS|ASSETFOLDERS|publish|PUBLISHFOLDERS" \
                  "<br>                                                                        |reference|REFFOLDERS" \
                  "<br>                                                                        |review|" \
                  "<br>                                                                        |work|WORKFOLDERS|images" \
                  "<br>                                                                        |maya|MAYAFOLDERS" \
                  "<br>                                                                        |zbrush|ZBRUSHFOLDERS</pre>" \
                  "<br>The main view will create a toolbar on the left for quick navigation to the specified rootFolders." \
                  "<br>The centralView is the main folder browser of the folder that exists on disk. You will be prompted to create a new project" \
                  "<br>if the base folder doesn't exist." \
                  "<br>" \
                  "<br>You can perform various rightClick options here, this will try to open various file formats using your system settings." \
                  "<br>In the systemFileBrowser.py valid = (\".ma\", \".mb\", \".obj\", \".jpg\", \".png\", \".ZPR\")" \
                  "<br>Using <b>Set As Root</b> will change the selected path as the root of the browser." \
                  "<br>Using <b> Explore to folder</b> will open a file explorer to that folder path." \
                  "<br>" \
                  "<br>This tool can be run standAlone via the exe, but can also be nested inside maya as a DockWidget using the sourceCode." \
                  "<h2>Schema.json Overview:</h2>" \
                  "<br>This is stored in a .json format in the configs folder. <br><b>Required data:</b>" \
                  "<table>" \
                  "<tr><td><b>\"projectName\"</b>:</td><td>&nbsp;&nbsp;This is the name of the project.</td></tr>" \
                  "<tr><td><b>\"projectPath\"</b>:</td><td>&nbsp;&nbsp;This is the root folder path on disk. eg: D:/myprojects/projectName" \
                  "<tr><td><b>\"configRoot\"</b>:</td><td>&nbsp;&nbsp;This is the base folder under the rootFolderPath for this config. eg: Assets" \
                  "<tr><td><b>\"ROOTS\":</b> {}</td><td>&nbsp;&nbsp;This is a dict of folder pairs. Roots tend to have None as their folder structure." \
                  "<tr><td><b>\"BASEFOLDERS\":</b> {}</td><td>&nbsp;&nbsp;This is the dict of the root folders that get created using the Create Fodlers button. " \
                  "<tr><td></td><td>&nbsp;&nbsp;The whole idea here is to be able to setup a subFolder schema of name \"SCHEMANAME\" and reuse that across the config." \
                  "<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;eg: \"BASEFOLDERS\": {\"Characters\": \"SCHEMANAME\"}" \
                  "<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;This way you can create fairly complex folder structures with minimal effort." \
                  "<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The create/update project schema UI can help you do this fairly quickly. " \
                  "</table>" \
                  "<h2>Create/Update Schema UI Overview:</h2>" \
                  "You can use this UI to setup a new project / folder schema to use. " \
                  "<br>" \
                  "<table>" \
                  "<tr><td><b><b>ProjectData:</b></td><td>This is where you set the base config name, pathTo and the base folderName." \
                  "<br>" \
                  "<tr><td><b>Load Schema</b></td><td>This is used to load an existing Schema config file for editing.</tr>" \
                  "<tr><td><b>Save Schema</b></td><td>This is used to save the layout to a config on disk.</td></tr>" \
                  "<tr><td><b>Create Schema:</b></td><td>This is layout of each of the schema widgets you can add folders to / right click assign existing schemas's as folders.</td></tr>" \
                  "<tr><td><b>Add SubFolder Schema:</b></td><td>Use this to add another subFolder schema layout to the main view.</td></tr>" \
                  "<tr><td><b>Preview Schema:</b></td><td>Use this to preview how the folders will be created on disk.</td></tr>" \
                  "</table>" \
                  "<br>Right clicking over a folder: subFolder pair will scan the current folderSchema's and allow you to rightClick assign one to the current pair to speed up the creation of the config." \
                  "<br>" \
                  "<hr>" \
                  "<h1>Hotkeys:</h1>" \
                  "<h3>Main Tree Browser:</h3>" \
                  "<table>" \
                  "<tr><td> &nbsp;&nbsp;<b>ctrl + leftclick  treeItem&nbsp;&nbsp;:</b></td><td>Expand to depth.</td></tr>" \
                  "<tr><td> &nbsp;&nbsp;<b>shft + leftclick  treeItem&nbsp;&nbsp;:</b></td><td>Collapse all under selected.</td></tr>" \
                  "<tr><td> &nbsp;&nbsp;<b>drag + control  treeItem&nbsp;&nbsp;:</b></td><td>Copy Dragged file instead of move.</td></tr>" \
                  "</table>" \
                  "</body>"

        self.label = QtWidgets.QTextEdit()
        self.label.setHtml(htmlStr)
        self.label.setReadOnly(True)

        self._mainLayout.addWidget(self.label)
        self.resize(1000, 1000)


if __name__ == "__main__":
    qtapp = QtWidgets.QApplication(sys.argv)
    win = HelpView(themeName="core", themeColor="")
    win.show()
    sys.exit(qtapp.exec_())
