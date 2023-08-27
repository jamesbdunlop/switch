from distutils.core import setup
from cx_Freeze import setup, Executable

dataFiles = [
    "D:\\CODE\\Python\\jamesd\\switch\\configs",
    "D:\\CODE\\Python\\jamesd\\switch\\readme.md",
]

setup(
    name="switch",
    version="0.1.0",
    author="James B Dunlop",
    author_email="james@anim83d.com",
    executables= [Executable("switch.py", icon="switch.ico", base = "Win32GUI")],
    options = {'build_exe': {'include_files':dataFiles, "silent":True,}},
)
