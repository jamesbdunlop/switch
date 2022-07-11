from distutils.core import setup
import py2exe

setup(name="switch",
      version="0.1",
      author="James B Dunlop",
      author_email="james@anim83d.com",
      packages=["configs", "services", "themes", "widgets"],
      data_files = [
      ('imageformats', [
        r'C:\Python\Python310\Lib\site-packages\PyQt5\Qt5\plugins\imageformats\qico.dll'
        ])],
      windows=[{
            "script": "switch.py",
            "icon_resources": [(1, "switch.ico")],
            "dest_base":"switch"}])