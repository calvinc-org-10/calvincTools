#################################################
# cSRF = calvincTools Simple Record Form classes
#################################################
# TODO: pretty up NEW RECORD FLAG

from enum import Enum
from typing import Dict, List

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QLineEdit, QMessageBox, QStatusBar, QWidget

from calvincTools.utils.cQWidgets import cComboBoxFromDict, cDataList
from calvincTools.utils.forms.definitions.cQFmConstants import cQFmConstants
from calvincTools.utils.forms.definitions.cQFormLayout import cQFormLayout
from calvincTools.utils.forms.definitions.cQFormFieldDef import cQFormFieldDef, cQFormFieldInstance
from calvincTools.utils.forms.definitions.cQFormBtnDef import cQFormBtnDef
from calvincTools.utils.forms.widgets.cQFmFldWidg import cQFmFldWidg
from calvincTools.utils.forms.widgets.cQFmLookupWidg import cQFmLookupWidg


class cSRF_FormUI_Base(QWidget):
    """
    UI only - no db functionality. For use in cQdbRecordForm classes to separate out UI code from db code. Not intended to be used on its own, but can be used as a base class for other UI classes if needed.

    Args:
        object (_type_): _description_
    """
    pages: List = []
    _page_spacing: int = 2

    def __init__(self,
        field_defs: List[cQFormFieldDef] | None = None,
        parent: QWidget | None = None,
        *args, **kwargs
        ):
        super().__init__(parent, *args, **kwargs)

        # set field definitions 
        if getattr(self, '_field_defs', None) is not None:
            # class-level wins
            pass
        elif field_defs is not None:
            self._field_defs = field_defs
        else:
            self._field_defs: List[cQFormFieldDef] = self.defineFields()
        # endif field_defs source
        self._validate_field_defs()
        self._field_defs_by_name = {d.name: d for d in self._field_defs}

        # build form layout
        self._layouts: cQFormLayout= self._buildFormLayout()

        self.pages = list(self.pages)  # copy if class-defined list to instance attribute
        self._buildPages()

        # Let subclass build its widgets into self.layoutForm
        self._formWidgets: Dict[str, cQFormFieldInstance] = {}
        self._lookupFrmElements: Dict[str, cQFmLookupWidg] = {}
        self._build_fields()

        # Add buttons
        self._addActionButtons()

        self.initialdisplay()

    # __init__

    ######################################################
    ########    property and key widget getters/setters

    ######################################################
    ########    Define form fields - to be implemented by subclass

    def defineFields(self):
        """Define the form fields.

        This method should be implemented by subclasses to define the form fields
        and their properties. It should populate self._field_defs with a list of cQFormFieldDef instances.
        """
        raise NotImplementedError
    # defineFields
    def _validate_field_defs(self):
        names = set()
        for d in self._field_defs:
            if d.name in names:
                raise ValueError(f"Duplicate field: {d.name}")
            names.add(d.name)
        # endfor each field def
    # _validate_field_defs

    ######################################################
    ########    Layout construction

    def _buildFormLayout(self) -> cQFormLayout:
        """
        Build the main layout, form layout, and button layout. Must be implemented by subclasses.
        Creates and configures:
        1. layoutMain: the main layout for the form (QVBoxLayout or QHBoxLayout)
        2. layoutForm: the grid layout for the form fields  (QTabWidget)
        3. layoutButtons: the layout for the action buttons (QHBoxLayout or QVBoxLayout)

        other Form elements created here:
        4. _statusBar: the status bar for the form (QStatusBar)
        5. _newrecFlag: the "New Record" flag label (QLabel)
        6. layoutFormHdr: the header layout for the form (QHBoxLayout)
        7. lblFormName: the form name label (cQFmNameLabel)
        8. Set the window title to the form name

        Returns:
            cQFormLayout: A structure containing the created layouts and widgets.

        """
        raise NotImplementedError

        ## see cSimpRecForm for an example implementation
        ##

    # _buildFormLayout

    def _buildPages(self) -> None:
        """Build the pages (tabs) for the form based on self.pages."""
        if self.numPages() < 1:
            # single page form
            self.pages = ['Main']
        # endif numPages

        self._page_map = {}

        for n, pg in enumerate(self.pages):
            pgnm = str(pg)
            widg, grid = QWidget(), QGridLayout()
            widg.setContentsMargins(0,0,0,0)
            grid.setContentsMargins(0,0,0,0)
            grid.setSpacing(self._page_spacing)
            widg.setLayout(grid)

            self._layouts.pages.addTab(widg, self.tr(pgnm))
            self._page_map[str(pgnm)] = grid
            # self._page_map[n] = grid
        # endfor page in self.pages
    # _buildPages
    def FormPage(self, idx: int | str | Enum) -> QGridLayout | None:
        def FormPageByName(name: str):
            return self._page_map.get(name, None)
        def FormPageByIndex(idx: int):
            if 0 <= idx < len(self.pages):
                return FormPageByName(self.pages[idx])
            elif idx in [const.value for const in cQFmConstants]:
                return FormPageSpecial(cQFmConstants(idx))
            return None
        def FormPageSpecial(enum: cQFmConstants):
            if enum is cQFmConstants.pageFixedTop:
                return self._layouts.fixed_top
            elif enum is cQFmConstants.pageFixedBottom:
                return self._layouts.fixed_bottom
            return None  # other enum values not valid pages
        ####################################
        ####################################
        # --- Enum handling ---
        if isinstance(idx, cQFmConstants):
            return FormPageSpecial(idx)

        # --- int index handling ---
        if isinstance(idx, int):
            return FormPageByIndex(idx)

        # --- str lookup ---
        if isinstance(idx, str):
            return FormPageByName(idx)

        return None
    # FormPage
    def numPages(self) -> int:
        """Return the number of pages/tabs in the form.

        Returns:
            int: Number of pages.
        """
        return len(self.pages)
        # or return self.layoutForm.count() # mebbe not - see _buildPages
    # numPages

    ######################################################
    ########    field and Widget placement

    def _build_fields(self):
        for defn in self._field_defs:
            widget = self._create_widget(defn)
            self._configure_widget(widget, defn)
            self._connect_widget(widget, defn)
            self._place_widget(widget, defn)

            self._formWidgets[defn.name] = cQFormFieldInstance(defn, widget)
            if defn.field_type == cQFormFieldDef.cQFormFieldType.LOOKUP:
                assert isinstance(widget, cQFmLookupWidg), "Lookup widget must be an instance of cQFmLookupWidg"
                self._lookupFrmElements[defn.name] = widget
        # endfor defn in self._field_defs
    # _build_fields
    def _create_widget(self, defn: cQFormFieldDef) -> QWidget:
        def _create_subform_widget(defn: cQFormFieldDef) -> QWidget:
            if defn.widget_type and issubclass(defn.widget_type, QWidget):
                widget = defn.widget_type(parent=self)
                return widget
            else:
                raise ValueError("subform_class must be specified for subform fields")
        def _create_lookup_widget(defn: cQFormFieldDef) -> QWidget:
            # TODO: cQFmLookupWidg gets ssnmkr, mdl the same way a cQFmFldWidg does
            widgType = defn.widget_type
            if widgType not in (cDataList, cComboBoxFromDict):
                widgType = cDataList  # force it to be a cDataList
            widget = cQFmLookupWidg(
                # chng cQFmLookupWidg to not get sessionmaker and model in __init__, but instead pass them in when reloading cxhoices, which is the only time they are actually needed, and will allow for more flexible use of the lookup widget in different contexts without having to worry about passing in the sessionmaker and model when creating the widget if they are not actually needed at that time - this will also make it easier to use the lookup widget in subforms where the sessionmaker and model may not be available at the time of widget creation, but can be passed in later when loading choices based on the parent record
                # session_factory=ssnmkr,
                # model=mdl,
                # lookup_field=defn.name,
                lblText=defn.label or defn.name,
                alignlblText=defn.label_alignment,
                lookupWidgType=widgType,
                choices=defn.choices,
                parent=self
            )
            return widget
            # endif lookupHandler
        def _create_scalar_widget(defn: cQFormFieldDef) -> QWidget:
            widget_type = defn.widget_type or QLineEdit

            return cQFmFldWidg(
                widgType=widget_type,
                lblText=defn.label or defn.name,
                alignlblText=defn.label_alignment,
                modlFld=defn.name,
                lblChkBxYesNo=defn.lblChkBxYesNo,
                choices=defn.choices,
                initval=defn.initval,
                parent=self
                )
        #######################################
        #######################################

        _widget_factory_map = {
            cQFormFieldDef.cQFormFieldType.LOOKUP: _create_lookup_widget,
            cQFormFieldDef.cQFormFieldType.SUBFORM:_create_subform_widget,
            cQFormFieldDef.cQFormFieldType.SCALAR: _create_scalar_widget,
            cQFormFieldDef.cQFormFieldType.INTERNAL: _create_scalar_widget,
        }
        factory = _widget_factory_map[defn.field_type]
        return factory(defn)
    # _create_widget
    def _configure_widget(self, widget: QWidget, defn: cQFormFieldDef):
        if defn.readonly and hasattr(widget, "setReadOnly"):
            widget.setReadOnly(True)    # type: ignore

        if defn.tooltip:
            widget.setToolTip(defn.tooltip)

        if defn.bg_color:
            widget.setStyleSheet(f"background-color: {defn.bg_color};")

        focusPolicy = defn.focus_policy
        if (defn.field_type in [
            cQFormFieldDef.cQFormFieldType.LOOKUP, cQFormFieldDef.cQFormFieldType.SUBFORM
            ]):
            focusPolicy = Qt.FocusPolicy.ClickFocus
        if focusPolicy:
            widget.setFocusPolicy(focusPolicy)

        if defn.readonly:
            if hasattr(widget, "setReadOnly"):
                widget.setReadOnly(True)    # type: ignore    
            else:
                widget.setProperty('readonly', True)
            #endif has setReadOnly
        #endif readonly

        if defn.maximum_width is not None:
            if hasattr(widget, "setMaximumWidth"):
                widget.setMaximumWidth(defn.maximum_width)
            else:
                widget.setProperty('maximumWidth', defn.maximum_width)
        if defn.maximum_height is not None:
            if hasattr(widget, "setMaximumHeight"):
                widget.setMaximumHeight(defn.maximum_height)
            else:
                widget.setProperty('maximumHeight', defn.maximum_height)
        #enddef maximum width/height
    # _configure_widget
    def _connect_widget(self, widget: QWidget, defn: cQFormFieldDef):
        if defn.field_type==cQFormFieldDef.cQFormFieldType.SCALAR and hasattr(widget, "signalFldChanged"):
            widget.signalFldChanged.connect(defn.on_change) if defn.on_change else None     # type: ignore

        if defn.field_type==cQFormFieldDef.cQFormFieldType.LOOKUP and isinstance(widget, cQFmLookupWidg):
            # TODO: use signalFldChanged for lookup widgets as well, and pass the field definition to the handler so that it can handle different lookup fields differently if needed, instead of having separate handlers for each lookup field - this will make the code cleaner and more scalable as we add more lookup fields - we can still have special handling within the handler based on the field definition as needed            
            lookupHandler = defn.on_change
            if lookupHandler:
                if isinstance(lookupHandler, str):
                    if not hasattr(widget, lookupHandler):
                        raise AttributeError(f"lookupHandler method '{lookupHandler}' not found in {widget.__class__.__name__}")
                    lookupHandler = getattr(widget, lookupHandler)
                if not callable(lookupHandler):
                    raise TypeError("lookupHandler must be a callable function or a string name of a method")
                widget.signalLookupSelected.connect(lookupHandler)
            # endif lookupHandler
        # endif lookup vs scalar
    # _connect_widget
    def _place_widget(self, widget: QWidget, defn: cQFormFieldDef):
        layout = self.FormPage(defn.page)
        if layout is None:
            raise ValueError(f"Invalid page {defn.page} for field {defn.name}")
        layout.addWidget(widget, *defn.position)    # type: ignore
    # _place_widget


    def defineActionButtons(self) -> List[cQFormBtnDef] | None:
        """
        Define Action Buttons to be added to Form
        """
        return None

    def _addActionButtons(self) -> None:
        """Add action buttons to the form.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError
        layoutButtons = self._layouts.buttons
    # _addActionButtons

    ######################################################
    ########    Display 

    def initialdisplay(self):
        """Initialize and display the first record or recordset

        Initializes a new record and loads the first record from the database.
        """
        raise NotImplementedError
    # initialdisplay

    def statusBar(self) -> QStatusBar|None:
        """Get the status bar."""
        return self.findChild(QStatusBar)
    # statusBar

    def showError(self, message: str, title: str = "Error") -> None:
        """Show an error message box."""
        QMessageBox.critical(self, title, message)
        # use status bar to show error message
        SB = self.statusBar()
        SB.showMessage(f"Error: {message}") if SB else None

        # TODO: choose whether to messageBox or status bar or both
    # showError

    ##########################################
    ########    Create

    ##########################################
    ########    Read

    ##########################################
    ########    Update

    # this is defined in the UI class because it needs to handle the field definitions and widgets, but it will likely call db methods defined in the db class to actually perform the updates. The field definitions can specify transform functions to handle any necessary transformations of the data before passing it to the db methods, and the on_change handlers can be used to trigger updates to other fields or UI elements as needed when a field value changes. Those functions can be defined in the UI class or the db class as needed, but the key point is that the field definitions allow for a lot of flexibility in how the form handles changes to field values, and the update logic can be distributed between the UI and db classes as needed to keep the code organized and maintainable.
    def _on_field_changed(self, widget, defn: cQFormFieldDef):
        value = widget.Value()

        if defn.transform:
            value = defn.transform(value)

        if defn.on_change:
            defn.on_change(value)
    # _on_field_changed

    ##########################################
    ########    Delete

# cSRF_FormUI_Base
    def endofclass(self):
        pass