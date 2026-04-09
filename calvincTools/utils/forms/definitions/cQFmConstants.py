from enum import Enum


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
    def endofclass(self):
        pass