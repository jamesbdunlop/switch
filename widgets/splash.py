import logging
from PySide2 import QtWidgets, QtCore
from widgets.base import BaseWidget as BaseWidget

logger = logging.getLogger(__name__)
logger.propagate = False
logging.basicConfig()


class SplashWidget(QtWidgets.QSplashScreen):
    def __init__(self, parent=None, pixmap=None, f=QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint) -> None:
        super(SplashWidget, self).__init__(parent=parent, pixmap=pixmap, f=f)
    