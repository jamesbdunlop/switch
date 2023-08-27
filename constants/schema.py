FOLDERNAME_BASE = "baseFolder"
FOLDERNAME_ROOT = "rootFolder"
INVALID_ROOTNAME = "INVALID - set ProjectRootFolderName in panel above."
IGNORES = ("projectName", "projectPath", "configRoot")
IGNORES_LINKED = ("projectName", "projectPath", "configRoot", "validExt", "BASEFOLDERS", "ROOTS")
EMPTY_CONFIG_DATA = {
    "projectName": "",
    "projectPath": "",
    "configRoot": "type project root name to update...",
    "ROOTS": {f"{FOLDERNAME_ROOT}01": None, f"{FOLDERNAME_ROOT}02": None, },
    "BASEFOLDERS": {f"{FOLDERNAME_BASE}01": ["LINKED01"], f"{FOLDERNAME_BASE}02": ["test"]},
    "LINKED01": {
        "photos": [None]
    },
    "LINKED02": {
        "supports": [None],
        "noSupports": [None]
    },
    "LINKED03": {
        "objs": ["LINKED02"],
        "maya": [None],
        "stl": ["LINKED02"]
    },
    "validExt": [".ma", ".mb", ".obj", ".jpg", ".png", ".ZPR", ".tif", ".tga", ".zpr", ".stl", ".ZTL", ".lys", ".dlp"],
}
SUBFOLDER_TITLE_NAME = "--SUBFOLDER-SCHEMAS-- (linkTo)"
DYN_ASSET_NAME = "---AssetName---"
READ_ONLY_NAMES = (DYN_ASSET_NAME, SUBFOLDER_TITLE_NAME)

