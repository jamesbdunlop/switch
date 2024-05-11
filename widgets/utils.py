import logging
from PySide6 import QtWidgets

logger = logging.getLogger(__name__)
logger.propagate = False
logging.basicConfig()


def createLabeledInput(name, placeHolderText="", toolTip=None):
    """Creates a QHBoxLayout with a QLabel and QLineEdit.

    Args:
        name (string):
            The name of the label
        placeHolderText (string):
            The text to put into the QLineEdit to indicate what to type
        toolTip (string):
            The text to use for the tool tip, this applies to the label and the lineEdit.

    Returns:
        QHBoxLayout, QLineEdit
    """
    layout = QtWidgets.QGridLayout()
    layout.setHorizontalSpacing(15)
    layout.setObjectName("{}_layout".format(name))

    label = QtWidgets.QLabel("{}: ".format(name))
    label.setObjectName("{}_label".format(name))

    lineEdit = QtWidgets.QLineEdit()
    lineEdit.setObjectName("{}_lineEdit".format(name))
    lineEdit.setPlaceholderText(placeHolderText)
    if toolTip is not None:
        label.setToolTip(toolTip)
        lineEdit.setToolTip(toolTip)

    layout.addWidget(label, 0, 0)
    layout.addWidget(lineEdit, 0, 1)

    return layout, lineEdit


def errorWidget(title, message):
    """Use for catching errors when files exist, or folders exist etc etc

    Args:
        title (string): Title of the widget
        message (string): Message of the widget
    """
    widget = QtWidgets.QErrorMessage()
    widget.setObjectName("ErrorDialog")
    widget.setWindowTitle(title)
    widget.showMessage(message)
    widget.exec_()
