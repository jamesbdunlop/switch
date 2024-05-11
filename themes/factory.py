import logging
import os, sys
import json
from PySide6 import QtCore

logger = logging.getLogger(__name__)
logger.propagate = False
logging.basicConfig()


def getPath():
    if not getattr(sys, "frozen", ""):
        PATH = os.path.dirname(__file__).replace("\\", "/")
        ICONPATH = "{}/iconpacks".format(os.path.dirname(__file__).replace("\\", "/"))
        return ICONPATH, PATH
    else:
        PATH = "{}/themes".format(os.path.dirname(sys.executable).replace("\\", "/"))
        ICONPATH = "{}/themes/iconpacks".format(
            os.path.dirname(sys.executable).replace("\\", "/")
        )
        return ICONPATH, PATH


# https://www.w3schools.com/colors/colors_monochromatic.asp
def loadTheme(name, data):
    iconPack = data.get("iconPack", "core")
    fontFamily = data.get("fontFamily", "Madan")
    fontBaseSize = data.get("fontBaseSize", "22px")
    fontHoverSize = data.get("fontHoverSize", "24px")
    fontTabSize = data.get("fontTabSize", "16px")
    fontColor = data.get("fontColor", "#FFFFFF")
    fontSelectedColor = data.get("fontSelectedColor", "#000000")
    level00 = data.get("level00", "#141B24")
    level01 = data.get("level01", "#23303E")
    level02 = data.get("level02", "#49627F")
    level03 = data.get("level03", "#7A95B3")
    level04 = data.get("level04", "#CDD7E2")
    hiLight = data.get("hiLight", "#8495A9")

    # dirPath = f"{PATH}{os.path.sep}{name}".replace("\\", "/")
    _, PATH = getPath()
    dirPath = "{}{}{}".format(PATH, os.path.sep, name).replace("\\", "/")

    lines = ""
    for eachFile in os.listdir(dirPath):
        if eachFile == "theme.json":
            continue

        # fp = QtCore.QFile(f"{dirPath}{os.path.sep}{eachFile}")
        fp = QtCore.QFile("{}{}{}".format(dirPath, os.path.sep, eachFile))
        fp.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)

        lines += QtCore.QTextStream(fp).readAll()
        lines = lines.replace("\n", "")
        # FONT FAMILY
        lines = lines.replace("$fontFamily", "{}".format(fontFamily))
        # FONT SIZES
        lines = lines.replace("$fontSize", "{}".format(fontBaseSize))
        lines = lines.replace("$fontHoverSize", "{}".format(fontHoverSize))
        lines = lines.replace("$fontTabSize", "{}".format(fontTabSize))
        lines = lines.replace("$fontColor", "{}".format(fontColor))
        lines = lines.replace("$fontSelectedColor", "{}".format(fontSelectedColor))
        # BASE COLORS
        lines = lines.replace("$level00", "{}".format(level00))
        lines = lines.replace("$level01", "{}".format(level01))
        lines = lines.replace("$level02", "{}".format(level02))
        lines = lines.replace("$level03", "{}".format(level03))
        lines = lines.replace("$level04", "{}".format(level04))
        lines = lines.replace("$hiLight", "{}".format(hiLight))
        # ICON PACKS
        lines = lines.replace(":/media", "{}/iconpacks/{}".format(PATH, iconPack))

    return lines


def fromJSON(themeName, themeColor):
    # dirPath = f"{PATH}{os.path.sep}{themeName}_{themeColor}"
    _, PATH = getPath()
    dirPath = "{}{}{}_{}".format(PATH, os.path.sep, themeName, themeColor)
    if not themeColor:
        # dirPath = f"{PATH}{os.path.sep}{themeName}"
        dirPath = "{}{}{}".format(PATH, os.path.sep, themeName)

    # theme = f"{dirPath}{os.path.sep}theme.json".replace("\\", "/")
    theme = "{}{}theme.json".format(dirPath, os.path.sep).replace("\\", "/")
    with open(theme) as f:
        data = json.load(f)

    return data


def toJSON(data, themeName, themeColor):
    _, PATH = getPath()
    dirPath = "{}{}{}_{}".format(PATH, os.path.sep, themeName, themeColor)
    if not themeColor:
        dirPath = "{}{}{}".format(PATH, os.path.sep, themeName)

    if not os.path.isdir(dirPath):
        os.makedirs(dirPath)

    filepath = "{}{}theme.json".format(dirPath, os.path.sep).replace("\\", "/")
    logger.debug("Saving config: %s", filepath)
    with open(filepath, "w") as outfile:
        outfile.write(json.dumps(data))


def getThemeData(themeName, themeColor):
    """

    :param themeName: `str` core name of the theme
    :param color: `str` of the variant eg `green` of `` for the base theme.
    :return: `str`
    """
    data = fromJSON(themeName, themeColor)

    return loadTheme(themeName, data)


if __name__ == "__main__":
    print(getThemeData("core", ""))
