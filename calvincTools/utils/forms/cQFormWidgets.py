
from enum import Enum

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QLabel, QWidget


class cQFmConstants(Enum):
    """Constants for form widget configurations."""
    # FldWidg_LineEdit = auto()
    # FldWidg_ComboBox = auto()
    # FldWidg_CheckBox = auto()
    # FldWidg_TextEdit = auto()
    # FldWidg_PlainTextEdit = auto()
    # FldWidg_DateEdit = auto()
    # FldWidg_DataList = auto()
    flagInternalVarField = '+'
    flagLookupField = '@'
    pageFixedTop = -1
    pageFixedBottom = -2
# endclass cQFmConstants

class cQFmNameLabel(QLabel):
    """A styled QLabel for displaying form titles.

    This label uses a distinctive font (Copperplate Gothic, 24pt) with a raised panel frame,
    suitable for form headers.
    """
    def __init__(self, formName:str = '', parent:QWidget|None = None):
        """Initialize the form name label.

        Args:
            formName (str, optional): Text to display as the form name. Defaults to ''.
            parent (QWidget | None, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)

        fontFormTitle = QFont()
        fontFormTitle.setFamilies([u"Copperplate Gothic"])
        fontFormTitle.setPointSize(24)
        self.setFont(fontFormTitle)
        self.setFrameShape(QFrame.Shape.Panel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWordWrap(True)

        if formName:
            self.setText(formName)
    # __init__
# endclass cQFmNameLabel


    