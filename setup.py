from distutils.core import setup
from cx_Freeze import setup, Executable

dataFiles = [
    "D:\\CODE\\Python\\jamesd\\switch\\configs",
    "D:\\CODE\\Python\\jamesd\\switch\\media",
    "D:\\CODE\\Python\\jamesd\\switch\\themes",
    "D:\\CODE\\Python\\jamesd\\switch\\readme.md",
    "D:\\CODE\\Python\\jamesd\\switch\\switchIcon.ico",
]

setup(
    name="switch",
    version="0.1.0",
    author="James B Dunlop",
    author_email="james@anim83d.com",
    executables= [Executable("switch.py", icon="switchIcon.ico", base = "Win32GUI")],
    options = {'build_exe': {'include_files':dataFiles, "silent":True,}},
)
