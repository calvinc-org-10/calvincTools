from dataclasses import dataclass, field
from typing import Any, Callable, Type

from PySide6.QtWidgets import QWidget

from .cQdbFormWidgets import cQFmFldWidg

@dataclass(frozen=True)
class cQFormFieldDef:
    name: str
    label: str | None = None
    widget_type: Type | None = None
    page: int | str = 0
    position: tuple[int, int, int, int] | tuple[int, int] = (0, 0)

    # behavior
    transform: Callable[[Any], Any] | None = None
    on_change: Callable[[Any], None] | None = None

    # UI options
    readonly: bool = False
    tooltip: str | None = None
    bg_color: str | None = None
    focus_policy: Any = None

    # special
    subform_class: Type | None = None


# runtime class to hold field definition and widget instance
class cQFormFieldInstance:
    def __init__(self, definition: cQFormFieldDef, widget: cQFmFldWidg):
        self.defn = definition
        self.widget = widget

    def get_value(self):
        return self.widget.Value()

    def set_value(self, val):
        self.widget.setValue(val)