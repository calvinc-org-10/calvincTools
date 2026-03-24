from dataclasses import dataclass, field
from typing import Any, Callable, Type, Dict
from enum import Enum

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

@dataclass(frozen=True)
class cQFormBtnDef:
    class SpacingFlag(Enum):
        NEW_HSECTION = ')*(newH'
        NEW_VSECTION = '=&&newV'
    name: str | SpacingFlag
    label: str = 'Button'
    label_alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignCenter
    icon: QIcon | None = None
    action: Callable | None = None

# cQFormBtnDef
