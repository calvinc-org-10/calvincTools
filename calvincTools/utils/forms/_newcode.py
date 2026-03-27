from typing import Any, Dict, List, Type
from functools import partial
from enum import Enum

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (QWidget,
    QLayout, QBoxLayout, QHBoxLayout, QVBoxLayout, QGridLayout, 
    QLabel, QLineEdit, QPushButton, 
    QTableView,
    QStatusBar, 
    QMessageBox, 
    )

from sqlalchemy import func, literal, select
from sqlalchemy.orm import (
    Session, sessionmaker,
    )
from sqlalchemy.sql.elements import ColumnElement

import qtawesome

from ..SQLAlcTools import get_primary_key_column
from ..cQWidgets import cComboBoxFromDict, cDataList, cGridWidget, cstdTabWidget
from ..messageBoxes import areYouSure
from ..strings import str2
from ..cQModels import SQLAlchemyTableModel
from .cQFormWidgets import cQFmConstants, cQFmNameLabel
from .cQdbFormWidgets import cQFmFldWidg, cQFmLookupWidg, cSimpRecFmElement_Base
from .cQFormFieldDef import cQFormFieldDef, cQFormFieldInstance
from .cQFormBtnDef import cQFormBtnDef
from .cQFormLayout import cQFormLayout

#################################################
# cSRF = calvincTools Simple Record Form classes
#################################################



# TODO: pretty up NEW RECORD FLAG
class cSRF_FormUI_Base(QWidget):
    """
    UI only - no db functionality. For use in cQdbRecordForm classes to separate out UI code from db code. Not intended to be used on its own, but can be used as a base class for other UI classes if needed.

    Args:
        object (_type_): _description_
    """
    pages: List = []

    def __init__(self, 
        field_defs: List[cQFormFieldDef] | None = None,
        parent: QWidget | None = None,
        *args, **kwargs
        ):
        super().__init__(parent, *args, **kwargs)

        # set field definitions 
        if self._field_defs is not None:
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
                idx = self.pages[idx]
            else:
                return None
            return self._page_map.get(idx, None)
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
            ssnmkr = self.ssnmaker()
            mdl = self.ORMmodel()
            assert ssnmkr is not None, "ssnmkr must be set before placing fields"
            assert mdl is not None, "ORMmodel must be set before placing fields"
            widgType = defn.widget_type
            if widgType not in (cDataList, cComboBoxFromDict):
                widgType = cDataList  # force it to be a cDataList
            widget = cQFmLookupWidg(
                session_factory=ssnmkr,
                model=mdl,
                lookup_field=defn.name,
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
            raise ValueError(f"Invalid page for field {defn.name}")
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

# cSRF_FormUI_Base

class cSRF_Formdb_Base(object):
    """
    db functionality only - no UI code. For use in cQdbRecordForm classes to separate out db code from UI code. Not intended to be used on its own, but can be used as a base class for other db classes if needed.

    Args:
        object (_type_): _description_
    """
    _ORMmodel:Type[Any]|None = None
    _primary_key: Any
    _currRecs: Any      # will be a single ORMRecord for SingleForm, List[ORMRecord] for MultiForm

    _ssnmaker:sessionmaker[Session]|None = None

    def __init__(self, 
        model: Type[Any]|None = None,
        ssnmaker: sessionmaker[Session] | None = None,
        *args, **kwargs
        ):
        super(cSRF_Formdb_Base, self).__init__(*args, **kwargs)
        
        # set model, primary key
        if self._ORMmodel is not None:
            # class-level wins
            pass
        elif model is not None:
            self.setORMmodel(model)
        else:
            raise ValueError("A model class must be provided either in the constructor or as a class attribute")
        self.setPrimary_key()

        # set ssnmaker
        if self._ssnmaker is not None:
            pass
        elif ssnmaker is not None:
            self.setssnmaker(ssnmaker)
        else:
            raise ValueError("A sessionmaker must be provided either in the constructor or as a class attribute")
        # endif ssnmaker
    # __init__
    
    ######################################################
    ########    property and key widget getters/setters

    def ORMmodel(self):
        """Get the ORM model class.

        Returns:
            Type[Any] | None: The SQLAlchemy ORM model class.
        """
        return self._ORMmodel

    def setORMmodel(self, model):
        """Set the ORM model class and update the primary key.

        Args:
            model: SQLAlchemy ORM model class.
        """
        self._ORMmodel = model
        self.setPrimary_key()

    def primary_key(self):
        """Get the primary key column.

        Returns:
            Primary key column object.
        """
        return self._primary_key

    def setPrimary_key(self):
        """Set the primary key from the ORM model.

        Raises:
            Exception: If ORMmodel is not set.
        """
        model = self.ORMmodel()
        if model is None:
            raise Exception('ORMmodel must be set first')
        # model is now narrowed to a non-None Type[Any]
        self._primary_key = get_primary_key_column(model)
    # get/set ORFMmodel/primary_key

    def ssnmaker(self):
        """Get the session maker.

        Returns:
            sessionmaker[Session] | None: Database session factory.
        """
        return self._ssnmaker

    def setssnmaker(self,ssnmaker):
        """Set the session maker.

        Args:
            ssnmaker: SQLAlchemy session maker.
        """
        self._ssnmaker = ssnmaker
    # get/set ssnmaker

    def currRec(self):
        """Get the current record.

        Returns:
            Current ORM record object.
        """
        return self._currRecs

    def setcurrRec(self, rec):
        """Set the current record.

        Args:
            rec: ORM record object to set as current.
        """
        self._currRecs = rec
    # get/set currRec

# cSRF_Formdb_Base
        

class cSRFSingleRecordForm(cSRF_FormUI_Base, cSRF_Formdb_Base):
    """
    Base class for single record forms. Inherits from both cSRF_FormUI_Base and cSRF_Formdb_Base to combine UI and db functionality.

    Args:
        cSRF_FormUI_Base (_type_): _description_
        cSRF_Formdb_Base (_type_): _description_
    """
    def __init__(self, *args, **kwargs):
        # allow for fieldDefs to be passed in as a kwarg, but default to None if not provided
        super().__init__(*args, **kwargs)

class cSRFMultiRecordWrapper(cSRF_FormUI_Base):
    """
    Base class for multi record wrapper forms. 
    Should contain at least one subform (cSRFRecordGrid or cSRFRecordList) in the fieldDefs, but can contain other widgets as well.
    Inherits from cSRF_FormUI_Base to provide UI functionality, but does not include any db functionality.

    Args:
        cSRF_FormUI_Base (_type_): _description_
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
class cSFRecordGrid(cSRF_Formdb_Base):
    """
    Base class for record grid subforms. Should be used as a subform within a cSRFMultiRecordWrapper. Inherits from cSRF_Formdb_Base to provide db functionality
    The UI functionality is provided by an SQLAlchemyTableModel and a QTableView.

    Args:
        cSRF_FormUI_Base (_type_): _description_
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
class cSRFRecordList(cSRFSingleRecordForm, cSRF_Formdb_Base):
    """
    Base class for record list subforms. Should be used as a subform within a cSRFMultiRecordWrapper. Inherits from both cSRF_FormUI_Base and cSRF_Formdb_Base to provide both UI and db functionality.
    The UI functionality is provided by a QListWidget.

    Args:
        cSRF_FormUI_Base (_type_): _description_
        cSRF_Formdb_Base (_type_): _description_
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# other form classes can be added here as needed, following the same pattern of inheriting from the appropriate base classes to combine UI and db functionality as needed.
# Note that a cSRFRecordGridForm = cSRFMultiRecordWrapper + cSRFRecordGrid is not necessary, as the cSRFRecordGrid can simply be used as a subform within the cSRFMultiRecordWrapper, and the cSRFMultiRecordWrapper can be used on its own as a wrapper for any number of subforms, including cSRFRecordGrids and cSRFRecordLists.
# similarly, a cSRFRecordListForm = cSRFMultiRecordWrapper + cSRFRecordList is not necessary, as the cSRFRecordList can simply be used as a subform within the cSRFMultiRecordWrapper, and the cSRFMultiRecordWrapper can be used on its own as a wrapper for any number of subforms, including cSRFRecordGrids and cSRFRecordLists.
