from dataclasses import dataclass, field

from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout, QHBoxLayout, QWidget, QGridLayout, QTabWidget, QBoxLayout, QStatusBar
    )

from .cQFormWidgets import cQFmNameLabel

@dataclass
class cQFormLayout:
    # Core containers
    main: QVBoxLayout
    header: QHBoxLayout
    form: QWidget
    fixed_top: QGridLayout
    pages: QTabWidget
    fixed_bottom: QGridLayout
    buttons: QBoxLayout
    status_bar: QStatusBar
    
    # UI widgets living in the layout
    lblFormName: cQFmNameLabel|None
    newrecFlag: QLabel|None
    
    