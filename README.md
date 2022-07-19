# switch
Small folder management system for windows projects at home

## Maya
Run the following inside Maya to create a dockable dockWidget.

````
import sys
import importlib
path = "D:\\CODE\\Python\\jamesd\\switch"
if path not in sys.path:
    sys.path.append(path)

from switch import switch as switch
importlib.reload(switch)
switch.run()
````

##Making standalone exe use 
````
python setup.py py2exe
````
in the switch folder. This will build into the dist folder.
Requirements will be valid paths for
````
('imageformats', [r'C:\Python\Python310\Lib\site-packages\PyQt5\Qt5\plugins\imageformats\qico.dll']),

('platforms', [r'C:\Python\Python310\Lib\site-packages\PyQt5\Qt5\plugins\platforms\qwindows.dll']),
````

Screenshots
-----------

The main UI<br>
![main_ui](media/main_ui_ss.png)

Adding folders using the createFolders button<br>
![main_ui](media/createFolders_ui_ss.png)

The config editor to quickly make the json files for the folder schema to use.<br>
![main_ui](media/createConfig_ui_ss.png)

Previewing the folders<br>
![main_ui](media/preview_ui_ss.png)

The help widget<br>
![main_ui](media/help_ui_ss.png)
