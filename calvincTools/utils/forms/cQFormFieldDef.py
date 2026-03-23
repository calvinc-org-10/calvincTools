from dataclasses import dataclass, field
from typing import Any, Callable, Type, Dict
from enum import Enum

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

from .cQFormWidgets import cQFmConstants

@dataclass(frozen=True)
class cQFormFieldDef:
    class cQFormFieldType(Enum):
        SCALAR = 'scalar'
        LOOKUP = 'lookup'
        SUBFORM = 'subform'
        INTERNAL = 'internal'  # for fields that are not database-associated, but are used for internal logic or UI management
    # cQFormFieldType
    
    name: str
    label: str | None = None
    label_alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft
    widget_type: Type | None = None
    
    choices: Dict | None = None
    initval: str = ''
    lblChkBxYesNo: dict[bool, str] | None = None
    
    page: int | str = 0
    position: tuple[int, int, int, int] | tuple[int, int] = (0, 0)

    # behavior
    transform: Callable[[Any], Any] | None = None
    on_change: Callable[[Any], None] | None = None

    # UI options
    readonly: bool = False
    tooltip: str | None = None
    maximum_width: int | None = None
    maximum_height: int | None = None
    bg_color: str | None = None
    focus_policy: Qt.FocusPolicy | None = None  # default focus policy will be ClickFocus for lookup and subform fields, None (i.e. inherit) for others

    # special
    lookup_handler: Callable[[Any], Any] | None = None
    subform_class: Type | None = None

    @property
    def field_type(self):
         if self.subform_class:
             return self.cQFormFieldType.SUBFORM
         elif any([
             callable(self.lookup_handler),
             self.name.startswith(cQFmConstants.flagLookupField.value),
             ]):
             return self.cQFormFieldType.LOOKUP
         elif self.name.startswith(cQFmConstants.flagInternalVarField.value):
            return self.cQFormFieldType.INTERNAL
         else:
             return self.cQFormFieldType.SCALAR
        # endif subform vs lookup vs scalar
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
