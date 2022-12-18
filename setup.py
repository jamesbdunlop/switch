from distutils.core import setup
import os
import py2exe

# Media files...
mediaFiles = list()
dir = r"D:\CODE\Python\jamesd\switch\media"
for file in os.listdir(dir):
    fp = "{}/{}".format(dir, file)
    if fp.endswith(".png"):
        mediaFiles.append(fp)

# Icon pack files...
iconPackFiles = list()
dir = r"D:\CODE\Python\jamesd\switch\themes\iconpacks\core"
for file in os.listdir(dir):
    fp = "{}/{}".format(dir, file)
    if fp.endswith(".png"):
        iconPackFiles.append(fp)

# Theme files
coreThemeFiles = list()
dir = r"D:\CODE\Python\jamesd\switch\themes\core"
for file in os.listdir(dir):
    fp = "{}/{}".format(dir, file)
    if fp.endswith(".qss") or fp.endswith(".json"):
        coreThemeFiles.append(fp)

# Configs
configFiles = list()
dir = r"D:\CODE\Python\jamesd\switch\configs"
for file in os.listdir(dir):
    fp = "{}/{}".format(dir, file)
    if fp.endswith(".json"):
        configFiles.append(fp)

dataFiles = [
    ("", [r"D:\CODE\Python\jamesd\switch\switch.ico"]),
    ("", [r"D:\CODE\Python\jamesd\switch\readme.md"]),
    (
        "imageformats",
        [
            r"C:\Python\Python310\Lib\site-packages\PyQt5\Qt5\plugins\imageformats\qico.dll"
        ],
    ),
    (
        "platforms",
        [
            r"C:\Python\Python310\Lib\site-packages\PyQt5\Qt5\plugins\platforms\qwindows.dll"
        ],
    ),
    ("themes\core_blue", [r"D:\CODE\Python\jamesd\switch\themes\core_blue\theme.json"]),
    (
        "themes\core_green",
        [r"D:\CODE\Python\jamesd\switch\themes\core_green\theme.json"],
    ),
]

dataFiles.append(("media", mediaFiles))
dataFiles.append(("themes\iconpacks\core", iconPackFiles))
dataFiles.append(("themes\core", coreThemeFiles))
dataFiles.append(("configs", configFiles))

setup(
    name="switch",
    version="0.0.2",
    author="James B Dunlop",
    author_email="james@anim83d.com",
    packages=["configs", "services", "themes", "widgets"],
    data_files=dataFiles,
    windows=[
        {
            "script": "switch.py",
            "icon_resources": [(1, "switch.ico")],
            "dest_base": "switch",
        }
    ],
)
