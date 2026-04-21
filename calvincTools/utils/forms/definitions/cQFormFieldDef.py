from dataclasses import dataclass, field
from typing import Any, Callable, Type, Dict, Literal
from enum import Enum

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

from .cQFmConstants import cQFmConstants

@dataclass(frozen=True)
class cQFormFieldDef:
    class cQFormFieldType(Enum):
        SCALAR = 'scalar'
        LOOKUP = 'lookup'
        SUBFORM = 'subform'
        INTERNAL = 'internal'  # for fields that are not database-associated, but are used for internal logic or UI management
    # cQFormFieldType
    
    name: str
    field_type: cQFormFieldType = cQFormFieldType.SCALAR
    label: str | None = None
    label_alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft
    widget_type: Type | None = None
    
    choices: Dict | Callable | None = None
    initval: str = ''
    lblChkBxYesNo: dict[bool, str] | None = None
    
    page: int | str | cQFmConstants = 0
    position: tuple[int, int, int, int] | tuple[int, int] = (0, 0)      # position is (row, column, rowspan, colspan) or (row, column)
    invisible: bool = False  # for fields that should not be rendered at all (e.g. password hash)

    # behavior
    transform: Callable[[Any], Any] | None = None
    on_change: Callable[..., None] | None = None

    # UI options
    readonly: bool = False
    tooltip: str | None = None
    minimum_width: int | None = None
    minimum_height: int | None = None
    maximum_width: int | None = None
    maximum_height: int | None = None
    bg_color: str | None = None
    frame: bool = True
    focus_policy: Qt.FocusPolicy | None = None  # default focus policy will be ClickFocus for lookup and subform fields, None (i.e. inherit) for others
    
    # for lookups
    depends_on: list[str] | None = None  # list of field names that this lookup depends on for its choices
# cQFormFieldDef

# runtime class to hold field definition and widget instance
class cQFormFieldInstance:
    def __init__(self, definition: cQFormFieldDef, widget: QWidget):
        self.defn = definition
        self.widget = widget

    def get_value(self):
        return self.widget.Value()  # type: ignore

    def set_value(self, val):
        self.widget.setValue(val)   # type: ignore
# cQFormFieldInstance
