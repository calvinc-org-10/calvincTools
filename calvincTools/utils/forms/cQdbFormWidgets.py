from collections.abc import Callable
from functools import partial
from typing import Any, Dict, List, Type

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QCheckBox, QComboBox, QDateEdit, QGridLayout, QLabel, QLineEdit, QPlainTextEdit, QPushButton, QTextEdit, QWidget
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from calvincTools.utils.cQWidgets import cComboBoxFromDict, cDataList
from calvincTools.utils.forms.cQFormWidgets import cQFmConstants
from calvincTools.utils.strings import str2


class cSimpRecFmElement_Base(QWidget):
    """Base class for form elements in simple record forms.

    This abstract base class defines the interface that all form elements must implement
    for loading from and saving to ORM records, as well as tracking dirty state.

    Signals:
        signalFldChanged: Emitted when the field value changes.
        dirtyChanged: Emitted when the dirty state changes.
    """
    signalFldChanged: Signal = Signal(object)
    dirtyChanged = Signal(bool)

    def loadFromRecord(self, rec: object) -> None:
        """Fill widget from ORM record.

        Args:
            rec: ORM record object to load data from.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError

    def saveToRecord(self, rec: object) -> None:
        """Push widget state into ORM record.

        Args:
            rec: ORM record object to save data to.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError

    def isDirty(self) -> bool:
        """Return True if the widget's value differs from what was loaded.

        Returns:
            bool: True if the value has been modified, False otherwise.
        """
        return False

    def setDirty(self, dirty: bool = True, sendSignal:bool = True) -> None:
        """Mark the field/subform as dirty.

        Args:
            dirty (bool, optional): Whether to mark as dirty. Defaults to True.
            sendSignal (bool, optional): Whether to emit dirtyChanged signal. Defaults to True.
        """
        pass
# endclass cSimpRecFmElement_Base

class cQFmFldWidg(cSimpRecFmElement_Base):
###########################################
# Improved cQFmFldWidg Class with Type Safety
    """A form field widget that wraps various Qt input widgets with a label.

    This class provides a unified interface for different types of input widgets
    (LineEdit, ComboBox, CheckBox, etc.) with automatic label placement and
    support for data binding to ORM models.

    Attributes:
        _wdgt (QWidget): The wrapped input widget.
        _label (QLabel | QCheckBox | None): The label widget.
        _modlField (str): Name of the ORM model field this widget represents.
    """
    _wdgt: QWidget
    _label: QLabel|QCheckBox|None = None
    _labelSetLblText: Callable[[str], None]|None = None
    _modlField: str = ''
    _lblChkYN: QLineEdit|None = None
    _lblChkYNValues: Dict[bool, str]|None = None

    # signalFldChanged: Signal = Signal(object)
    # dirtyChanged = Signal(bool)

    def __init__(
        self,
        widgType: Type[QWidget],
        lblText: str = ' ',
        lblChkBxYesNo: Dict[bool, str]|None = None,
        alignlblText: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft,
        modlFld: str = '',
        choices: Dict | List | Callable | None = None,
        initval: str = '',
        parent: QWidget|None = None,
    ):
        """Initialize a form field widget.

        Args:
            widgType (Type[QWidget]): Type of widget to create (QLineEdit, QComboBox, etc.).
            lblText (str, optional): Label text. Defaults to ' '.
            lblChkBxYesNo (Dict[bool, str] | None, optional): For checkboxes, maps bool to display text.
            alignlblText (Qt.AlignmentFlag, optional): Label alignment. Defaults to AlignLeft.
            modlFld (str, optional): ORM model field name. Defaults to ''.
            choices (Dict | List | None, optional): Choices for combo boxes or data lists. Defaults to None.
            initval (str, optional): Initial value. Defaults to ''.
            parent (QWidget | None, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)

        # Create the widget with proper typing
        self._wdgt = self.createWidget(widgType, choices, initval)
        lblText = self.tr(lblText)

        # Set up widget-specific behaviors with proper type checking
        self._setup_widget_behavior(widgType, lblText, lblChkBxYesNo)

        # Set the ModelField
        self.setModelField(modlFld)

        # Set up the layout
        self._setup_layout(widgType, lblText, alignlblText, lblChkBxYesNo)
    # __init__

    def createWidget(
        self,
        widgType: Type[QWidget],
        choices: Dict | List | Callable | None = None,
        initval: str = ''
    ) -> QWidget:
        """Create the appropriate widget based on type."""
        if callable(choices):
            choice_listdict:Dict|List|None = choices()
        else:
            choice_listdict = choices
        # endif callable choices
        if issubclass(widgType, cComboBoxFromDict):
            if not isinstance(choice_listdict, dict):
                # raise TypeError("Expected choices to be a dictionary for cComboBoxFromDict")
                choice_listdict = {}
            return widgType(choice_listdict, self)
        elif issubclass(widgType, cDataList):
            if not isinstance(choice_listdict, (dict)):
                # raise TypeError("Expected choices to be a dictionary or list for cDataList")
                choice_listdict = {}
            return widgType(choice_listdict, initval, self)
        elif issubclass(widgType, QComboBox):
            wdgt = widgType(self)
            if choice_listdict is not None:
                if isinstance(choice_listdict, dict):
                    for key, value in choice_listdict.items():
                        wdgt.addItem(str(value), key)
                else:
                    wdgt.addItems([str(item) for item in choice_listdict])
            return wdgt
        else:
            return widgType(self)
        # endif widgType class
    # createWidget

    def _setup_widget_behavior(
        self,
        widgType: Type[QWidget],
        lblText: str,
        lblChkBxYesNo: Dict[bool, str]|None = None
    ) -> None:
        """Configure widget-specific behaviors with proper type checking."""
        wdgt = self._wdgt

        if issubclass(widgType, cDataList):
            self._setup_datalist_behavior(wdgt, lblText)
        elif issubclass(widgType, QLineEdit):
            self._setup_lineedit_behavior(wdgt, lblText)
        elif issubclass(widgType, (QTextEdit, QPlainTextEdit)):
            self._setup_textedit_behavior(wdgt, lblText)
        elif issubclass(widgType, (cComboBoxFromDict, QComboBox)):
            self._setup_combobox_behavior(wdgt, lblText)
        elif issubclass(widgType, QDateEdit):
            self._setup_dateedit_behavior(wdgt, lblText)
        elif issubclass(widgType, QCheckBox):
            self._setup_checkbox_behavior(wdgt, lblText, lblChkBxYesNo)
        elif issubclass(widgType, QLabel):
            self._setup_label_behavior(wdgt, lblText)
        elif issubclass(widgType, QPushButton):
            self._setup_pushbutton_behavior(wdgt, lblText)
        else:
            raise TypeError(f'type {widgType} is not implemented')
    # _setup_widget_behavior


    def _setTextstring(self, widget: QWidget, text: Any) -> None:
        """If the widget has a setText method, call it with a string."""
        setter = getattr(widget, "setText", None)
        if callable(setter):
            setter(str2(text))  # cast to str to be safe
    # _setTextstring

    def _setup_datalist_behavior(self, wdgt: cDataList|QWidget, lblText: str) -> None:
        """Configure behavior for cDataList widgets."""
        if not isinstance(wdgt, cDataList):
            raise TypeError("Expected a cDataList widget")
        self._label = QLabel(lblText)
        self.LabelText = self._label.text
        self._labelSetLblText = partial(self._setTextstring, self._label)
        self._label.setBuddy(wdgt)

        self.Value = wdgt.selectedItem
        # self.setValue = partial(self._setTextstring, wdgt)
        self.setValue = self._create_datalist_setter(wdgt)
        self.addChoices = wdgt.addChoices
        wdgt.editingFinished.connect(self.fldChanged)
    # _setup_datalist_behavior
    def _create_datalist_setter(self, wdgt:cDataList|QWidget) -> Callable[[Any], None]:
        """Create a type-safe setter function for cDataList."""
        if not isinstance(wdgt, (cDataList, )):
            raise TypeError("Expected a cDataList widget")
        def set_datalist_value(value: Any) -> None:
            # value could be the actual data value, or the display text
            # assume key value first
            if value in wdgt.choices:
                wdgt.setText(wdgt.choices[value])
                return
            elif str(value) in wdgt.choices.values():
                wdgt.setText(str(value))
                return
            else:
                wdgt.setText(str(value))
                return
            #endif
        return set_datalist_value
    # _create_datalist_setter

    def _setup_lineedit_behavior(self, wdgt: QLineEdit|QWidget, lblText: str) -> None:
        """Configure behavior for QLineEdit widgets."""
        if not isinstance(wdgt, QLineEdit):
            raise TypeError("Expected a QLineEdit widget")
        self._label = QLabel(lblText)
        self.LabelText = self._label.text
        self._labelSetLblText = partial(self._setTextstring, self._label)
        self._label.setBuddy(wdgt)

        self.Value = wdgt.text
        self.setValue = partial(self._setTextstring, wdgt)
        wdgt.editingFinished.connect(self.fldChanged)
    # _setup_lineedit_behavior

    def _setup_label_behavior(self, wdgt: QLabel|QWidget, lblText: str) -> None:
        """Configure behavior for QLabel widgets."""
        if not isinstance(wdgt, QLabel):
            raise TypeError("Expected a QLabel widget")
        self._label = QLabel(lblText)
        self.LabelText = self._label.text
        self._labelSetLblText = partial(self._setTextstring, self._label)
        self._label.setBuddy(wdgt)

        self.Value = wdgt.text
        self.setValue = partial(self._setTextstring, wdgt)
    # _setup_label_behavior

    def _setup_textedit_behavior(self, wdgt: QTextEdit|QPlainTextEdit|QWidget, lblText: str) -> None:
        """Configure behavior for text edit widgets."""
        if not isinstance(wdgt, (QTextEdit, QPlainTextEdit)):
            raise TypeError("Expected a QTextEdit or QPlainTextEdit widget")
        self._label = QLabel(lblText)
        self.LabelText = self._label.text
        self._labelSetLblText = partial(self._setTextstring, self._label)
        self._label.setBuddy(wdgt)

        self.Value = wdgt.toPlainText
        self.setValue = wdgt.setPlainText
        wdgt.textChanged.connect(self.fldChanged)
    # _setup_textedit_behavior

    def _setup_combobox_behavior(self, wdgt: cComboBoxFromDict|QComboBox|QWidget, lblText: str) -> None:
        """Configure behavior for combo box widgets."""
        if not isinstance(wdgt, (cComboBoxFromDict, QComboBox)):
            raise TypeError("Expected a cComboBoxFromDict or QComboBox widget")
        self._label = QLabel(lblText)
        self.LabelText = self._label.text
        self._labelSetLblText = partial(self._setTextstring, self._label)
        self._label.setBuddy(wdgt)

        self.Value = wdgt.currentData
        self.setValue = self._create_combobox_setter(wdgt)

        if isinstance(wdgt, cComboBoxFromDict):
            self.replaceDict = wdgt.replaceDict

        wdgt.activated.connect(self.fldChanged)
    # _setup_combobox_behavior
    def _create_combobox_setter(self, wdgt:cComboBoxFromDict|QComboBox|QWidget) -> Callable[[Any], None]:
        """Create a type-safe setter function for combo boxes."""
        if not isinstance(wdgt, (cComboBoxFromDict, QComboBox)):
            raise TypeError("Expected a cComboBoxFromDict or QComboBox widget")
        def set_combobox_value(value: Any) -> None:
            if wdgt.findData(value) == -1:
                wdgt.setCurrentText(str(value))
            else:
                wdgt.setCurrentIndex(wdgt.findData(value))
        return set_combobox_value
    # _create_combobox_setter

    def _setup_dateedit_behavior(self, wdgt: QDateEdit|QWidget, lblText: str) -> None:
        """Configure behavior for date edit widgets."""
        if not isinstance(wdgt, QDateEdit):
            raise TypeError("Expected a QDateEdit widget")
        self._label = QLabel(lblText)
        self.LabelText = self._label.text
        self._labelSetLblText = partial(self._setTextstring, self._label)
        self._label.setBuddy(wdgt)

        self.Value = lambda: wdgt.date().toPython()
        self.setValue = wdgt.setDate
        wdgt.userDateChanged.connect(self.fldChanged)
    # _setup_dateedit_behavior

    def _setup_checkbox_behavior(
        self,
        wdgt: QCheckBox|QWidget,
        lblText: str,
        lblChkBxYesNo: Dict[bool, str]|None = None
    ) -> None:
        """Configure behavior for checkbox widgets."""
        if not isinstance(wdgt, QCheckBox):
            raise TypeError("Expected a QCheckBox widget")
        self._label = wdgt
        wdgt.setText(lblText)
        self.LabelText = wdgt.text
        self._labelSetLblText = partial(self._setTextstring, wdgt)

        self.Value = wdgt.isChecked
        self.setValue = lambda value: wdgt.setChecked(value if isinstance(value, bool) else False)

        if lblChkBxYesNo:
            self._lblChkYNValues = lblChkBxYesNo
            self._lblChkYN = QLineEdit()
            self._lblChkYN.setProperty('noedit', True)
            self._lblChkYN.setReadOnly(True)
            self._lblChkYN.setFrame(False)
            self._lblChkYN.setMaximumWidth(40)
            self._lblChkYN.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        wdgt.checkStateChanged.connect(self.fldChanged)
    # _setup_checkbox_behavior

    def _setup_pushbutton_behavior(self, wdgt: QPushButton|QWidget, lblText: str) -> None:
        """Configure behavior for pushbutton widgets."""
        if not isinstance(wdgt, QPushButton):
            raise TypeError("Expected a QPushButton widget")
        # self._label = QLabel(lblText)
        self._label = None
        wdgt.setText(lblText)
        self.LabelText = wdgt.text
        self._labelSetLblText = partial(self._setTextstring, wdgt)

        self.icon = wdgt.icon
        self.setIcon = wdgt.setIcon

        self.Value = wdgt.text
        self.setValue = partial(self._setTextstring, wdgt)

        wdgt.clicked.connect(self.fldChanged)
        pass
    # _setup_pushbutton_behavior

    def _setup_layout(
        self,
        widgType: Type[QWidget],
        lblText: str,
        alignlblText: Qt.AlignmentFlag,
        lblChkBxYesNo: Dict[bool, str]|None = None
    ) -> None:
        """Configure the layout based on widget type and alignment."""
        layout = QGridLayout()

        # Determine widget positions based on alignment
        if alignlblText == Qt.AlignmentFlag.AlignLeft:
            positions = ((0, 0), (0, 1))
        elif alignlblText == Qt.AlignmentFlag.AlignRight:
            positions = ((0, 1), (0, 0))
        elif alignlblText == Qt.AlignmentFlag.AlignTop:
            positions = ((0, 0), (1, 0))
        elif alignlblText == Qt.AlignmentFlag.AlignBottom:
            positions = ((1, 0), (0, 0))
        else:
            positions = ((0, 0), (0, 1))  # default to left

        # Place widgets in layout
        if issubclass(widgType, QCheckBox):
            if lblChkBxYesNo and self._lblChkYN:
                layout.addWidget(self._lblChkYN, *positions[0])
                layout.addWidget(self._wdgt, *positions[1])
            else:
                layout.addWidget(self._wdgt, 0, 0)
        else:
            if lblText and self._label:
                layout.addWidget(self._label, *positions[0])
                layout.addWidget(self._wdgt, *positions[1])
            else:
                layout.addWidget(self._wdgt, 0, 0)

        self.setLayout(layout)
    # _setup_layout

    def setLabelText(self, txt: str) -> None:
        """Set the label text if a label exists."""
        if self._labelSetLblText is not None:
            self._labelSetLblText(txt)
            if self._label is not None:
                self._label.repaint()
    # setLabelText

    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to the contained widget."""
        return getattr(self._wdgt, name, None)

    def modelField(self) -> str:
        """Get the model field name."""
        return self._modlField

    def setModelField(self, fldName: str) -> None:
        """Set the model field name."""
        self._modlField = fldName

    def isInternalVarField(self) -> bool:
        """Check if the field is an internal variable field."""
        return self._modlField.startswith(cQFmConstants.flagInternalVarField.value)

    # ------------------------------
    # Internal helpers
    # ------------------------------

    def loadFromRecord(self, rec):
        """Load the ORM record value into the widget."""
        if not self.isInternalVarField():
            val = getattr(rec, self._modlField, None) if rec else None
            self._setWidgetValue(val)
            self._loaded_value = val
            self.setDirty(False, sendSignal=False)
        # endif internal var field
    # loadFromRecord

    def saveToRecord(self, rec):
        """Write widget value back into ORM record, if dirty."""
        if not self.isDirty() or self.isInternalVarField():
            return
        new_val = self._getWidgetValue()
        setattr(rec, self._modlField, new_val)
        self._loaded_value = new_val
        self.setDirty(False, sendSignal=False)
    # saveToRecord

    def isDirty(self) -> bool:
        """Check if this field widget has unsaved changes.

        Returns:
            bool: True if the current value differs from the loaded value.
        """
        # if self.isInternalVarField():
        #     return False
        # if widg is None:
        #     widg = self
        # return widg._dirty
        return self._loaded_value_changed
    # isDirty

    def setDirty(self, dirty: bool|None = None, sendSignal:bool = True) -> None:
        """Set the dirty state of this field widget.

        Args:
            dirty (bool, optional): Whether to mark as dirty. If not given, dirty flag is not changed. Defaults to None.
            sendSignal (bool, optional): Whether to emit dirtyChanged signal. Defaults to True.
        """
        # if self.isInternalVarField():
        #     self._dirty = False
        #     return
        # if self._dirty == dirty:
        #     return
        # self._dirty = dirty

        # sometimes we want to force the dirty flag even if value matches
        if isinstance(dirty, bool):
            self._loaded_value_changed = dirty

        # Only emit signal if becoming dirty
        if self.isDirty() and sendSignal:
            # self.dirtyChanged.emit(dirty)
            self.dirtyChanged.emit(True)
            # endif dirty
    # setDirty

    def _setWidgetValue(self, val):
        """Best-effort assignment based on widget type."""
        self.setValue(val)

    def _getWidgetValue(self):
        """Best-effort retrieval based on widget type."""
        return self.Value()

    @Slot()
    def fldChanged(self, *args: Any) -> None:
        """Handle field change events."""
        if self._lblChkYNValues and self._lblChkYN:
            # Update the check box label if configured
            newstate = (args[0] == Qt.CheckState.Checked) if args else False
            self._lblChkYN.setText(self._lblChkYNValues[newstate])

        # new_val = self._getWidgetValue()
        self.setDirty(dirty=True)
        self.signalFldChanged.emit(args if args else (None,))
    # fldChanged
# endclass cQFmFldWidg


class cQFmLookupWidg(cSimpRecFmElement_Base):
    """A lookup widget that allows selection from database values.

    This widget provides a dropdown or auto-complete interface populated with
    distinct values from a database field. It supports both cDataList and
    cComboBoxFromDict widget types.

    Attributes:
        _session_factory (sessionmaker[Session]): Database session factory.
        _model: The ORM model class to lookup from.
        _lookup_field (str): Name of the field to lookup.

    Signals:
        signalLookupSelected: Emitted when a lookup value is selected.
    """
    """
    returns a widget that allows the user to select from a list of values
    returns the text selected, not the key

    NOTE: any choices passed in will be overwritten when refreshChoices() is called

    """
    signalLookupSelected: Signal = Signal(object)

    def __init__(
        self,
        lblText: str|None = None,
        alignlblText: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft,
        lookupWidgType: Type[QWidget] = cDataList,
        choices: Dict | List | Callable | None = {},
        parent: QWidget | None = None,
    ):
        """Initialize a lookup widget.

        Args:
            session_factory (sessionmaker[Session]): Database session factory.
            model (type[Any]): ORM model to look up values from.
            lookup_field (str): Field name to look up.
            lblText (str | None, optional): Label text. Defaults to None (uses field name).
            alignlblText (Qt.AlignmentFlag, optional): Label alignment. Defaults to AlignLeft.
            lookupWidgType (Type[QWidget], optional): Widget type. Defaults to cDataList.
            choices (Dict | None, optional): Initial choices. Defaults to {}.
            parent (QWidget | None, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        # self._session_factory = session_factory
        # self._model = model
        # self._lookup_field = lookup_field
        # if lblText is None:
        #     lblText = lookup_field.replace('_', ' ').title()

        # Create the widget with proper typing
        if not issubclass(lookupWidgType, (cComboBoxFromDict, cDataList)):
            lookupWidgType = cDataList  # force it to be a cDataList
        self._wdgt = self.createWidget(lookupWidgType, choices)
        lblText = str2(lblText, ValueTransforms={None:lambda:'UNKNOWN'})
        lblText = self.tr(lblText)

        # Set up widget-specific behaviors with proper type checking
        self._setup_widget_behavior(lblText)

        # Set up the layout
        self._setup_layout(lblText, alignlblText)

        self._choices = choices
        self.refreshChoices()
    # __init__

    def getrawChoices(self) -> Dict | List | Callable | None:
        """Get the raw choices data structure."""
        return self._choices
    def getChoices(self) -> Dict | List | None:
        """Get the processed choices as a dictionary, if applicable."""
        choices = self.getrawChoices()
        if callable(choices):
            return choices()
        if isinstance(choices, (dict, list)):
            return choices
        return None
    # getChoices

    def createWidget(self, widgType: Type[QWidget], choices: Dict | List | Callable | None = {}) -> QWidget:
        """Create the widget with the specified type, choices, and initial value."""
        initval = ''
        if callable(choices):
            choice_listdict:Dict|List|None = choices()
        else:
            choice_listdict = choices
        # endif callable choices

        if issubclass(widgType, cDataList):
            if isinstance(choice_listdict, list):
                # convert list to dict with same keys and values
                choice_listdict = {str(item): str(item) for item in choice_listdict}
            if not isinstance(choice_listdict, (dict)):
                # raise TypeError("Expected choices to be a dictionary or list for cDataList")
                choice_listdict = {}
            return widgType(choice_listdict, initval, self)
        elif issubclass(widgType, cComboBoxFromDict):
            if not isinstance(choice_listdict, dict):
                # raise TypeError("Expected choices to be a dictionary for cComboBoxFromDict")
                choice_listdict = {}
            return widgType(choice_listdict, self)
        else:
            return cDataList({}, '', self)
        # endif widgType class
    # createWidget

    def _setup_widget_behavior(self, lblText: str) -> None:
        """Configure widget-specific behaviors with proper type checking."""
        wdgt = self._wdgt
        widgType = type(wdgt)

        if issubclass(widgType, cDataList):
            self._setup_datalist_behavior(wdgt, lblText)
        elif issubclass(widgType, (cComboBoxFromDict, QComboBox)):
            self._setup_combobox_behavior(wdgt, lblText)
        else:
            raise TypeError(f'type {widgType} is not implemented')
        # endif widget type
    # _setup_widget_behavior

    def _create_datalist_setter(self, wdgt:cDataList|QWidget) -> Callable[[Any], None]:
        """Create a type-safe setter function for cDataList."""
        if not isinstance(wdgt, (cDataList, )):
            raise TypeError("Expected a cDataList widget")
        def set_datalist_value(value: Any) -> None:
            # value could be the actual data value, or the display text
            # assume key value first
            if value in wdgt.choices:
                wdgt.setText(wdgt.choices[value])
                return
            elif str(value) in wdgt.choices.values():
                wdgt.setText(str(value))
                return
            else:
                wdgt.setText(str(value))
                return
            #endif
        return set_datalist_value
    # _create_datalist_setter
    def _setup_datalist_behavior(self, wdgt: cDataList|QWidget, lblText: str) -> None:
        """Configure behavior for cDataList widgets."""
        if not isinstance(wdgt, cDataList):
            raise TypeError("Expected a cDataList widget")
        self._label = QLabel(lblText)
        self.LabelText = self._label.text
        self._labelSetLblText = self._label.setText
        self._label.setBuddy(wdgt)

        self.Value = wdgt.selectedItem
        self.setValue = self._create_datalist_setter(wdgt)
        self.addChoices = wdgt.addChoices
        wdgt.editingFinished.connect(self._emitSelection)
    # _setup_datalist_behavior

    def _create_combobox_setter(self, wdgt:cComboBoxFromDict|QComboBox|QWidget) -> Callable[[Any], None]:
        """Create a type-safe setter function for combo boxes."""
        if not isinstance(wdgt, (cComboBoxFromDict, QComboBox)):
            raise TypeError("Expected a cComboBoxFromDict or QComboBox widget")
        def set_combobox_value(value: Any) -> None:
            if wdgt.findData(value) == -1:
                wdgt.setCurrentText(str(value))
            else:
                wdgt.setCurrentIndex(wdgt.findData(value))
        return set_combobox_value
    def _setup_combobox_behavior(self, wdgt: cComboBoxFromDict|QComboBox|QWidget, lblText: str) -> None:
        """Configure behavior for combo box widgets."""
        if not isinstance(wdgt, (cComboBoxFromDict, QComboBox)):
            raise TypeError("Expected a cComboBoxFromDict or QComboBox widget")
        self._label = QLabel(lblText)
        self.LabelText = self._label.text
        self._labelSetLblText = self._label.setText
        self._label.setBuddy(wdgt)

        self.Value = wdgt.currentData
        self.setValue = self._create_combobox_setter(wdgt)

        if isinstance(wdgt, cComboBoxFromDict):
            self.replaceDict = wdgt.replaceDict

        wdgt.activated.connect(self._emitSelection)
    # _setup_combobox_behavior

    def _setup_layout(
        self,
        lblText: str,
        alignlblText: Qt.AlignmentFlag,
    ) -> None:
        """Configure the layout based on widget type and alignment."""
        layout = QGridLayout()

        # Determine widget positions based on alignment
        if alignlblText == Qt.AlignmentFlag.AlignLeft:
            positions = ((0, 0), (0, 1))
        elif alignlblText == Qt.AlignmentFlag.AlignRight:
            positions = ((0, 1), (0, 0))
        elif alignlblText == Qt.AlignmentFlag.AlignTop:
            positions = ((0, 0), (1, 0))
        elif alignlblText == Qt.AlignmentFlag.AlignBottom:
            positions = ((1, 0), (0, 0))
        else:
            positions = ((0, 0), (0, 1))  # default to left
        # Place widgets in layout
        if lblText and self._label:
            layout.addWidget(self._label, *positions[0])
            layout.addWidget(self._wdgt, *positions[1])
        else:
            layout.addWidget(self._wdgt, 0, 0)

        self.setLayout(layout)
    # _setup_layout

    @Slot()
    def refreshChoices(self, 
        ) -> None:
        """Reload available values from the database.

        Fetches distinct values from the lookup field and updates the widget's choices.
        """
        values = self.getChoices()
        if values is None:
            values = []

        # Populate the list
        if isinstance(self._wdgt, cDataList):
            self._wdgt.clear()
            self._wdgt.addChoices({val: str(val) for val in values if val is not None})
        if isinstance(self._wdgt, cComboBoxFromDict):
            self._wdgt.replaceDict({str(val): val for val in values if val is not None})
    # refreshChoices            

    def _setWidgetValue(self, val):
        """Best-effort assignment based on widget type."""
        self.setValue(val)

    def _getWidgetValue(self):
        """Best-effort retrieval based on widget type."""
        return self.Value()

    def loadFromRecord(self, val):  # type: ignore
        """Load the ORM record value into the widget."""
        self._setWidgetValue(val)
        # no setting dirty for lookups

    def saveToRecord(self, rec):
        """Save the lookup widget value to a record.

        Args:
            rec: ORM record object.

        Note:
            Lookups don't save their values to the record, so this is a no-op.
        """
        # lookups don't save their values to the record
        return

    # lookups don't become dirty
    def isDirty(self, widg = None):
        """Check if the lookup widget is dirty.

        Returns:
            bool: Always returns False since lookups don't track dirty state.
        """
        if widg is None:
            widg = self
        return False

    def setDirty(self, dirty:bool = False, sendSignal:bool = False):
        """Set the dirty state of the lookup widget.

        Args:
            dirty (bool, optional): Dirty state. Defaults to False.
            sendSignal (bool, optional): Whether to emit signal. Defaults to False.

        Note:
            Lookups don't maintain dirty state, so this is a no-op.
        """
        return

    @Slot()
    def _emitSelection(self) -> None:
        """Emit the selected value."""
        value = None
        if isinstance(self._wdgt, (cComboBoxFromDict, QComboBox)):
            value = self._wdgt.currentData()
        elif isinstance(self._wdgt, cDataList):
            value = self._wdgt.selectedItem()
        self.signalLookupSelected.emit(value)
    # _emitSelection
# endclass cQFmLookupWidg

