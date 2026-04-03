from calvincTools.utils.cQWidgets import cComboBoxFromDict, cDataList
from calvincTools.utils.forms.widgets.cSimpRecFmElement_Base import cSimpRecFmElement_Base
from calvincTools.utils.strings import str2


from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QComboBox, QGridLayout, QLabel, QWidget


from collections.abc import Callable
from typing import Any, Dict, List, Type


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
    def endofclass(self):
        pass