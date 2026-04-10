from dataclasses import dataclass, field
from typing import Any, Callable, Type, Dict
from enum import Enum

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

@dataclass(frozen=True)
class cQFormBtnDef:
    class ButtonType(Enum):
        NORMAL = '(!normal=)'
        NEW_HSECTION = ')*(newH'
        NEW_VSECTION = '=&&newV'
    name: str = ''
    type: ButtonType = ButtonType.NORMAL
    text: str = 'Button'
    # text_alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignCenter   # nope, can't set button text alignments
    icon: QIcon | None = None
    commitBtn: bool = False
    action: Callable | None = None

# cQFormBtnDef
