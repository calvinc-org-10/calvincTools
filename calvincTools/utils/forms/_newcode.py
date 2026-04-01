from typing import Any, Dict, List, Type, Callable
from functools import partial
from enum import Enum

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (QWidget,
    QLayout, QBoxLayout, QHBoxLayout, QVBoxLayout, QGridLayout, 
    QLabel, QLineEdit, QPushButton, 
    QTableView, QListWidget, QListWidgetItem,
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
                if idx in [const.value for const in cQFmConstants]:
                    return FormPageSpecial(cQFmConstants(idx))
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

class cSRF_Formdb_Base(object):
    """
    db functionality only - no UI code. For use in cQdbRecordForm classes to separate out db code from UI code. Not intended to be used on its own, but can be used as a base class for other db classes if needed.

    Args:
        object (_type_): _description_
    """
    _ORMmodel:Type[Any]|None = None
    _primary_key: Any
    _currRec: Any      # will be a single ORMRecord for SingleForm, List[ORMRecord] for MultiForm

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
        return getattr(self, '_currRec', None)

    def setcurrRec(self, rec):
        """Set the current record.

        Args:
            rec: ORM record object to set as current.
        """
        self._currRec = rec
    # get/set currRec
    

    ##########################################
    ########    Create

    ##########################################
    ########    Read

    ##########################################
    ########    Update

    ##########################################
    ########    Delete


# cSRF_Formdb_Base
        

class cSRFSingleRecordForm(cSRF_FormUI_Base, cSRF_Formdb_Base):
    """
    Base class for single record forms. Inherits from both cSRF_FormUI_Base and cSRF_Formdb_Base to combine UI and db functionality.
    
    children must implement:
    Define form fields - to be implemented by subclass

    def defineFields(self):
        Define the form fields.

        This method should be implemented by subclasses to define the form fields
        and their properties. It should populate self._field_defs with a list of cQFormFieldDef instances.

    """
    def __init__(self, 
        formname: str|None = None,
        field_defs: List[cQFormFieldDef] | None = None,
        model: Type[Any]|None = None,
        ssnmaker: sessionmaker[Session] | None = None,
        parent: QWidget | None = None,
        *args, **kwargs):

        self._formname = getattr(self, '_formname', None)
        if not self._formname:
            self._formname = formname if formname else 'Form'

        super().__init__(field_defs=field_defs, model=model, ssnmaker=ssnmaker, parent=parent, *args, **kwargs)
    # __init__

    ######################################################
    ########    Layout construction

    def _buildFormLayout(self) -> cQFormLayout:
        """Build the form layout for cSimpleRecordForm.

        Returns:
            QFormLayout instance
        """

        layoutMain = QVBoxLayout(self)
        layoutFormHdr = QHBoxLayout()
        layoutForm = cGridWidget(scrollable=True)
        layoutFormFixedTop = QGridLayout()
        layoutFormPages = cstdTabWidget()
        layoutFormFixedBottom = QGridLayout()
        layoutButtons = QVBoxLayout()  # may get redefined in _addActionButtons
        statusBar = QStatusBar(self)

        # should this be in _finalizeMainLayout instead?
        layoutForm.addLayout(layoutFormFixedTop, 0, 0)
        layoutForm.addWidget(layoutFormPages, 1, 0)
        layoutForm.addLayout(layoutFormFixedBottom, 2, 0)

        assert isinstance(self._formname, str), "_formname must be set before building form layout"
        lblFormName = cQFmNameLabel(self.tr(self._formname), self)
        layoutFormHdr.addWidget(lblFormName)

        newrecFlag = QLabel("New Record", self)
        fontNewRec = QFont()
        fontNewRec.setBold(True)
        fontNewRec.setPointSize(10)
        fontNewRec.setItalic(True)
        newrecFlag.setFont(fontNewRec)
        newrecFlag.setStyleSheet("color: red;")
        layoutFormHdr.addWidget(newrecFlag)

        # put it together
        layoutMain.addLayout(layoutFormHdr)
        layoutMain.addWidget(layoutForm)
        layoutMain.addLayout(layoutButtons)
        layoutMain.addWidget(statusBar)

        self.setWindowTitle(self.tr(self._formname))

        rtnval = cQFormLayout(
            main=layoutMain,
            header=layoutFormHdr,
            form=layoutForm,
            fixed_top=layoutFormFixedTop,
            pages=layoutFormPages,
            fixed_bottom=layoutFormFixedBottom,
            buttons=layoutButtons,
            status_bar=statusBar,
            
            lblFormName = lblFormName,
            newrecFlag = newrecFlag,
            )

        return rtnval
    # _buildFormLayout

    ######################################################
    ########    field and Widget placement

    def defineActionButtons(self):
        _iconlib = qtawesome.icon
        r = [
            cQFormBtnDef(text="First", icon=_iconlib("mdi.page-first"), action=self.on_loadfirst_clicked),
            cQFormBtnDef(text="Previous", icon= _iconlib("mdi.arrow-left-bold"), action=self.on_loadprev_clicked),
            cQFormBtnDef(text="Next", icon=_iconlib("mdi.arrow-right-bold"), action=self.on_loadnext_clicked),
            cQFormBtnDef(text="Last", icon=_iconlib("mdi.page-last"), action=self.on_loadlast_clicked),
            cQFormBtnDef(type=cQFormBtnDef.ButtonType.NEW_HSECTION),
            cQFormBtnDef(text="Add", icon=_iconlib("mdi.plus"), action=self.on_add_clicked),
            cQFormBtnDef(text="Save", icon=_iconlib("mdi.content-save"), commitBtn=True, action=self.on_save_clicked),
            cQFormBtnDef(text="Delete", icon=_iconlib("mdi.delete"), action=self.on_delete_clicked),
            cQFormBtnDef(text="Cancel", icon=_iconlib("mdi.cancel"), action=self.on_cancel_clicked),
            ]
        return r

    def _addActionButtons(self,
            ActionButtons:List[cQFormBtnDef]|None = None,
            ) -> None:
        """Add action buttons to the form.
        """

        Actns = ActionButtons if ActionButtons is not None else self.defineActionButtons()
        if Actns is None:
            return

        layoutButtons = self._layouts.buttons

        innerLayout = QHBoxLayout()

        for btndef in Actns:
            if btndef.type == cQFormBtnDef.ButtonType.NEW_VSECTION:
                layoutButtons.addLayout(innerLayout)
                innerLayout = QHBoxLayout()
            elif btndef.type == cQFormBtnDef.ButtonType.NEW_HSECTION:
                innerLayout.addSpacing(20)
            elif btndef.type != cQFormBtnDef.ButtonType.NORMAL:
                raise ValueError(f"unknown button type {btndef.type}")
            else:
                btn = QPushButton(btndef.text)
                if btndef.icon is not None:
                    btn.setIcon(btndef.icon)
                if callable(btndef.action):
                    btn.clicked.connect(btndef.action)
                if btndef.commitBtn:
                    self.btnCommit = btn
                innerLayout.addWidget(btn)
            # endif button type
        # endfor btndef om Actns
        layoutButtons.addLayout(innerLayout)
    # _addNavButtons

    ######################################################
    ########    Display 

    def initialdisplay(self):
        """Initialize and display the first record.

        Initializes a new record and loads the first record from the database.
        """
        self.initializeRec()
        self.on_loadfirst_clicked()
    # initialdisplay()

    def fillFormFromcurrRec(self):
        """Load the current record into all form fields.

        Updates all field widgets with values from the current record
        and updates the dirty and new record flags.
        """
        for widgStructure in self._formWidgets.values():
            widg = widgStructure.widget
            if isinstance(widg, cSimpRecFmElement_Base):
                widg.loadFromRecord(self.currRec())

        self.showNewRecordFlag()
        self.showCommitButton()
        # self.setDirty(False) - nope, don't need to set form dirty state here - isDirty checks individual fields
    # fillFormFromRec

    # TODO: wrap with fillFormFromcurrRec
    # TODO: play with positioning of new record flag
    def showNewRecordFlag(self) -> None:
        """Show or hide the 'New Record' flag based on current record state."""
        nrf = getattr(self, '_newrecFlag', None)
        if not isinstance(nrf, QWidget):
            return
        nrf.setVisible(self.isNewRecord())

    def showCommitButton(self) -> None:
        """Show the commit button if the record is dirty."""
        btnCommit = getattr(self, 'btnCommit', None)
        if not isinstance(btnCommit, QWidget):
            return
        btnCommit.setEnabled(self.isDirty())
    # showCommitButton

    ##################################################
    ########    Record Navigation 

    def isit_OKToLeaveRecord(self) -> bool:
        """
        Check if the form is dirty. If so, prompt user.
        Returns True if it is safe to proceed with navigation, False otherwise.
        """
        if not self.isDirty():
            return True

        choice = areYouSure(
            self,
            "Unsaved changes",
            "You have unsaved changes. Save before continuing?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Yes,
            )

        if choice == QMessageBox.StandardButton.Yes:
            self.on_save_clicked()
            return True

        elif choice == QMessageBox.StandardButton.No:
            # Discard changes -> reload current record fresh
            if self.currRec():
                self.fillFormFromcurrRec()
            return True

        else:  # Cancel
            return False
    # isit_OKToLeaveRecord

    def _navigate_to(self, rec_id: int):
        """Navigate safely to a record (with save/discard prompt if dirty)."""
        if not self.isit_OKToLeaveRecord():
            return  # Cancel pressed → stay put

        self._load_record_by_id(rec_id)
    # _navigate_to

    def get_prev_record_id(self, recID:int) -> int:
        """Get the ID of the previous record.

        Args:
            recID (int): Current record ID.

        Returns:
            int: ID of the previous record, or None if no previous record exists.
        """
        ssnmkr = self.ssnmaker()
        assert ssnmkr is not None, "Sessionmaker must be set before touching the database"
        pKey = self.primary_key()
        with ssnmkr() as session:
            prev_id = session.query(func.max(pKey)).where(pKey < recID).scalar()
        return prev_id
    def get_next_record_id(self, recID:int) -> int:
        """Get the ID of the next record.

        Args:
            recID (int): Current record ID.

        Returns:
            int: ID of the next record, or None if no next record exists.
        """
        ssnmkr = self.ssnmaker()
        pKey = self.primary_key()
        assert ssnmkr is not None, "Sessionmaker must be set before touching the database"
        with ssnmkr() as session:
            next_id = session.query(func.min(pKey)).where(pKey > recID).scalar()
        return next_id

    def on_loadfirst_clicked(self):
        """Load the first record in the database."""
        # determine minimum id in database and load it
        ssnmkr = self.ssnmaker()
        pKey = self.primary_key()
        assert ssnmkr is not None, "Sessionmaker must be set before touching the database"
        with ssnmkr() as session:
            min_id = session.query(func.min(pKey)).scalar()
            if min_id:
                self._navigate_to(min_id)

    def on_loadprev_clicked(self):
        """Load the previous record in the database."""
        # determine previous id in database and load it
        currRec = self.currRec()
        pKey = self.primary_key()
        currID = getattr(currRec, pKey.key)
        prev_id = self.get_prev_record_id(currID)
        if prev_id:
            self._navigate_to(prev_id)

    def on_loadnext_clicked(self):
        """Load the next record in the database."""
        # determine next id in database and load it
        currRec = self.currRec()
        pKey = self.primary_key()
        currID = getattr(currRec, pKey.key)
        next_id = self.get_next_record_id(currID)
        if next_id:
            self._navigate_to(next_id)

    def on_loadlast_clicked(self):
        """Load the last record in the database."""
        # determine maximum id in database and load it
        ssnmkr = self.ssnmaker()
        pKey = self.primary_key()
        assert ssnmkr is not None, "Sessionmaker must be set before touching the database"
        with ssnmkr() as session:
            max_id = session.query(func.max(pKey)).scalar()
            if max_id:
                self._navigate_to(max_id)

    ##########################################
    ########    Create

    def initializeRec(self, initializeTo=None):
        """
        Initialize a new record with default values.

        implementation should call fillFormFromcurrRec() after setting default values in self.currRec
        """
        modlType = self.ORMmodel() if initializeTo is None else initializeTo
        assert modlType is not None, "ORMmodel must be set before initializing record"
        self.setcurrRec(modlType())
    # initializeRec

    def on_add_clicked(self):
        """
        Add a new record to the database: initialize, set defaults and save.
        No, don't save. reserve that for the save button.
        """
        # if dirty, ask to save
        if not self.isit_OKToLeaveRecord():
            return

        self.initializeRec()
        self.fillFormFromcurrRec()
    # add_record

    ##########################################
    ########    Read

    # # --- Lookup navigation ---
    def _load_record_by_id(self, pk_val):
        """Low-level load (assumes it's safe to replace current record)."""
        ssnmkr = self.ssnmaker()
        assert ssnmkr is not None, "Sessionmaker must be set before touching the database"
        with ssnmkr() as session:
            modl = self.ORMmodel()
            assert modl is not None, "ORMmodel must be set before loading record"
            rec = session.get(modl, pk_val)
            if rec is None:
                self.showError(f"No Record with id {pk_val}")
                return
            else:
                # detach rec from session and make it the current record
                session.expunge(rec)
                self.setcurrRec(rec)
                self.fillFormFromcurrRec()
            # endif rec 
        #endwith session
    # load_record_by_id

    def load_record(self, recindex: int):
        """
        Load a record from the database.
        NOTE: For this class, recindex is the id of the record to load, not the index.

        Args:
            recindex (int): The ID of the record to load.
        """
        self._load_record_by_id(recindex)
    # load_record

    def load_record_by_field(self, field: str | Any, value: Any) -> None:
        """
        field may be either:
          - a string (column name), or
          - an ORM field object (MyModel.name).
        """
        if not self.isit_OKToLeaveRecord():
            return  # Cancel pressed → stay put

        if isinstance(field, str):
            orm_field = getattr(self._ORMmodel, field)
        else:
            orm_field = field

        ssnmkr = self.ssnmaker()
        assert ssnmkr is not None, "Sessionmaker must be set before touching the database"
        with ssnmkr() as session:
            modl = self.ORMmodel()
            assert modl is not None, "ORMmodel must be set before loading record"
            rec = session.query(modl).filter(orm_field == value).first()
            if rec is None:
                self.showError(f"No Record with {orm_field.key} == {value}")
                return
            else:
                # detach rec from session and make it the current record
                session.expunge(rec)
                self.setcurrRec(rec)
                self.fillFormFromcurrRec()
            # endif rec 
        #endwith session
    # load_record_by_field

    @Slot()
    def lookup_and_load(self, fld: str, value: Any):
        """Load a record by looking up a field value.

        Args:
            fld (str): Field name to search.
            value (Any): Value to search for (can be dict with 'text' key, or plain value).
        """
        value = value.get('text', value) if isinstance(value, dict) else (getattr(value, 'text', value) if hasattr(value, 'text') else value)
        self.load_record_by_field(fld, value)
    # lookup_CIMSNum

    ##########################################
    ########    Update

    @Slot()
    def _on_field_changed(self, widget, defn: cQFormFieldDef):
        value = widget.Value()

        if defn.transform:
            value = defn.transform(value)

        if defn.on_change:
            defn.on_change(value)
        
        self.showCommitButton()
    # _on_field_changed
        
    @Slot()
    def on_save_clicked(self, *_):
        """
        Collects field values from adapters/subforms, writes them into currRec,
        and persists via a short-lived session.
        """
        currRec = self.currRec()
        if not currRec:
            return

        try:
            # Push data from form -> ORM object, except for subforms - they must come after the main record is saved
            # for fldName, fldDef in self._field_defs_by_name.items():
            for fldName, fldStruct in self._formWidgets.items():
                fldDef = fldStruct.defn
                widget = fldStruct.widget
                isSubFormElmnt = fldDef.field_type == cQFormFieldDef.cQFormFieldType.SUBFORM
                if not isSubFormElmnt:      # subforms handled after main record is saved
                    if isinstance(widget, cSimpRecFmElement_Base):
                        widget.saveToRecord(currRec)
            # endfor fldDef in self.fieldDefs

            # Persist using a short-lived session
            ssnmkr = self.ssnmaker()
            assert ssnmkr is not None, "Sessionmaker must be set before touching the database"
            with ssnmkr(expire_on_commit=False) as session:
                merged = session.merge(currRec)
                session.flush()
                session.refresh(merged)

                pKey = self.primary_key()
                recID = getattr(merged, pKey.key)   # no change for existing record; loads new id for a new one
                # should I copy other fields, too?

                # session.expunge(self.currRec) # not needed, since self.currRec not bound to session

                session.commit()
            # endwith session

            # now handle subforms
            # for fldName, fldDef in self._field_defs_by_name.items():
            for fldName, fldStruct in self._formWidgets.items():
                fldDef = fldStruct.defn
                widget = fldStruct.widget
                isSubFormElmnt = fldDef.field_type == cQFormFieldDef.cQFormFieldType.SUBFORM
                if isSubFormElmnt:
                    if isinstance(widget, cSimpRecFmElement_Base):
                        widget.saveToRecord(currRec)
            # endfor fldDef in self.fieldDefs

            # reload the record (repaints screen, gets db defaults and new id, if any)
            self.repopLookups()
            self._load_record_by_id(recID)

            # all this not needed because of reload
            # # Reset dirty flags (both form and adapters)
            # for fldName, fldDef in self.fieldDefs.items():
            #     widget = fldDef.get("widget")
            #     if widget:
            #         widget.setDirty(False)
            # self.setDirty(self, False)

            # # Clear new record flag
            # assert not self.isNewRecord()
            # self.showNewRecordFlag(False)

        except Exception as e:
            self.showError(str(e), "Error saving record")
    # on_save_clicked

    ##########################################
    ########    Delete

    # TODO: confirm delete
    @Slot()
    def on_delete_clicked(self):
        """Handle delete button click.

        Prompts for confirmation, then deletes the current record and navigates
        to a neighboring record.
        """
        currRec = self.currRec()
        if not currRec:
            return

        pKey = self.primary_key()
        keyID = getattr(currRec, pKey.key)

        if not self.isit_OKToLeaveRecord():
            return  # Cancel pressed → stay put

        confirm = areYouSure(
            self,
            "Delete record",
            f"Really delete record {keyID}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        # Actually delete
        ssnmkr = self.ssnmaker()
        assert ssnmkr is not None, "Sessionmaker must be set before touching the database"
        modl = self.ORMmodel()
        assert modl is not None, "ORMmodel must be set before deleting record"
        with ssnmkr() as session:
            rec = session.get(modl, keyID)
            if rec:
                session.delete(rec)
                session.commit()

        self.repopLookups()
        # Navigate to neighbor, or clear form if none
        next_id = self.get_next_record_id(keyID)
        prev_id = self.get_prev_record_id(keyID)
        target_id = next_id or prev_id
        if target_id:
            self._load_record_by_id(target_id)
        else:
            self.initializeRec()
            self.fillFormFromcurrRec()
    # on_delete_clicked

    # ##########################################
    # ########    Record Status

    def isNewRecord(self) -> bool:
        """Check if the current record is a new (unsaved) record.

        Returns:
            bool: True if the current record has no primary key value, False otherwise.
        """
        pKey = self.primary_key()
        currRec = self.currRec()
        return currRec is None or getattr(currRec, pKey.key) is None

    @Slot()
    def setDirty(self, dirty: bool|None = None):
        """Poll children for dirty state and update save button."""
        # removed code to set dirty state of children, since each adapter handles its own dirty state internally and the form's dirty state is determined by polling the children when needed

        # Enable save button if anything is dirty
        btnCommit = getattr(self, 'btnCommit', None)
        if hasattr(btnCommit, 'setEnabled'):
            btnCommit.setEnabled(self.isDirty()) # type: ignore
    # setFormDirty

    def isDirty(self) -> bool:
        """Check if any form element is dirty."""
        # any() stops and returns True as soon as it finds the first True
        return any(el.widget.isDirty() for el in self._formWidgets.values())       # type: ignore
    # isDirty

    def on_cancel_clicked(self):
        """Handle the Cancel button click by closing the form.

        Note:
            Currently just closes the form without any confirmation.
        """
        #for now, just close form
        self.close()
    # cancel_record

    def repopLookups(self) -> None:
        """Refresh all lookup widgets with current database values."""
        for lkupname, lkupwdgt in self._lookupFrmElements.items():
                lkupwdgt.refreshChoices()   # type: ignore
    # repopLookups

    ###############################################
    ###############################################
    # TO BE ADDED LATER:
    def beforeLoad(self, rec): pass
    def afterLoad(self, rec): pass
    def beforeSave(self): pass
    def afterSave(self): pass

# cSRFSingleRecordForm

class cSRFMultiRecordWrapper(cSRF_FormUI_Base):
    """
    Base class for multi record wrapper forms. 
    Should contain at least one subform (cSRFRecordGrid or cSRFRecordList) in the fieldDefs, but can contain other widgets as well.
    Inherits from cSRF_FormUI_Base to provide UI functionality, ***but does not include any db functionality.***

    Args:
        cSRF_FormUI_Base (_type_): _description_
    """
    def __init__(self, 
        formname: str|None = None,
        field_defs: List[cQFormFieldDef] | None = None,
        parent: QWidget | None = None,
        *args, **kwargs):

        self._formname = getattr(self, '_formname', None)
        if not self._formname:
            self._formname = formname if formname else 'Form'

        super().__init__(field_defs=field_defs, parent=parent, *args, **kwargs)
    # __init__

    ######################################################
    ########    Layout construction

    def _buildFormLayout(self) -> cQFormLayout:
        """Build the form layout for cSimpleRecordForm.

        Returns:
            QFormLayout instance
        """

        layoutMain = QVBoxLayout(self)
        layoutFormHdr = QHBoxLayout()
        layoutForm = cGridWidget(scrollable=True)
        layoutFormFixedTop = QGridLayout()
        layoutFormPages = cstdTabWidget()
        layoutFormFixedBottom = QGridLayout()
        layoutButtons = QVBoxLayout()  # may get redefined in _addActionButtons
        statusBar = QStatusBar(self)

        # should this be in _finalizeMainLayout instead?
        layoutForm.addLayout(layoutFormFixedTop, 0, 0)
        layoutForm.addWidget(layoutFormPages, 1, 0)
        layoutForm.addLayout(layoutFormFixedBottom, 2, 0)

        assert isinstance(self._formname, str), "_formname must be set before building form layout"
        lblFormName = cQFmNameLabel(self.tr(self._formname), self)
        layoutFormHdr.addWidget(lblFormName)

        newrecFlag = QLabel("New Record", self)
        fontNewRec = QFont()
        fontNewRec.setBold(True)
        fontNewRec.setPointSize(10)
        fontNewRec.setItalic(True)
        newrecFlag.setFont(fontNewRec)
        newrecFlag.setStyleSheet("color: red;")
        layoutFormHdr.addWidget(newrecFlag)

        # put it together
        layoutMain.addLayout(layoutFormHdr)
        layoutMain.addWidget(layoutForm)
        layoutMain.addLayout(layoutButtons)
        layoutMain.addWidget(statusBar)

        self.setWindowTitle(self.tr(self._formname))

        rtnval = cQFormLayout(
            main=layoutMain,
            header=layoutFormHdr,
            form=layoutForm,
            fixed_top=layoutFormFixedTop,
            pages=layoutFormPages,
            fixed_bottom=layoutFormFixedBottom,
            buttons=layoutButtons,
            status_bar=statusBar,
            
            lblFormName = lblFormName,
            newrecFlag = newrecFlag,
            )

        return rtnval
    # _buildFormLayout

    ######################################################
    ########    field and Widget placement

    def defineActionButtons(self):
        _iconlib = qtawesome.icon
        r = [
            cQFormBtnDef(text="Close", icon=_iconlib("mdi.cancel"), action=self.on_close_clicked),
            ]
        return r

    def _addActionButtons(self,
            ActionButtons:List[cQFormBtnDef]|None = None,
            ) -> None:
        """Add action buttons to the form.
        """

        Actns = ActionButtons if ActionButtons is not None else self.defineActionButtons()
        if Actns is None:
            return

        layoutButtons = self._layouts.buttons

        innerLayout = QHBoxLayout()

        for btndef in Actns:
            if btndef.type == cQFormBtnDef.ButtonType.NEW_VSECTION:
                layoutButtons.addLayout(innerLayout)
                innerLayout = QHBoxLayout()
            elif btndef.type == cQFormBtnDef.ButtonType.NEW_HSECTION:
                innerLayout.addSpacing(20)
            elif btndef.type != cQFormBtnDef.ButtonType.NORMAL:
                raise ValueError(f"unknown button type {btndef.type}")
            else:
                btn = QPushButton(btndef.text)
                if btndef.icon is not None:
                    btn.setIcon(btndef.icon)
                if callable(btndef.action):
                    btn.clicked.connect(btndef.action)
                if btndef.commitBtn:
                    self.btnCommit = btn
                innerLayout.addWidget(btn)
            # endif button type
        # endfor btndef om Actns
    # _addNavButtons

    def on_close_clicked(self):
        """Handle the Cancel button click by closing the form.

        Note:
            Currently just closes the form without any confirmation.
        """
        #for now, just close form
        self.close()
    # cancel_record


    ######################################################
    ########    Display 

    def initialdisplay(self):
        """
        Initialize and display the form.
        """
        # self.initializeRec()
        # self.on_loadfirst_clicked()
        ...
    # initialdisplay()

# cSRFSingleRecordForm
        
class cSRFRecordGrid(cSRF_Formdb_Base, cSimpRecFmElement_Base):
    """
    Base class for record grid subforms. Should be used as a subform within a cSRFMultiRecordWrapper. Inherits from cSRF_Formdb_Base to provide db functionality
    The UI functionality is provided by an SQLAlchemyTableModel and a QTableView.

    # like cSimpleRecordSubForm1, but *may or may not* depend on a parent record

    This widget displays related records in a table format with add/delete functionality.

    Presents subrecords as a Table

    Attributes:
        _ORMmodel (Type[Any]): ORM model for the subrecords.
        _primary_key: Primary key of the subrecord model.
        _parentFK: Foreign key field linking to the parent record. May be none if no parent record.
        _ssnmaker: Database session factory.
        _parentRec: Reference to the parent record. May be None
        _childRecs (list): List of child records.
        _deleted_childRecs (list): List of child records pending deletion.

    Args:
        ORMmodel (Type[Any]): ORM model for the subrecords
        parentFK (InstrumentedAttribute): relationship FK field in the parent model. May be None
        session_factory (sessionmaker): SQLAlchemy sessionmaker
        parent (QWidget | None): parent widget
    """

    def __init__(self,
        ORMmodel: Type[Any]|None = None,
        linkFld: Any = None,
        parent_linkFld: Any = None,
        session_factory: sessionmaker[Session] | None = None,
        viewClass: Type[QTableView] = QTableView,
        parent=None,
        *args, **kwargs):
        """Initialize a table-based subform.

        Args:
            ORMmodel (Type[Any] | None, optional): ORM model for subrecords. Defaults to None.
            linkFld: Any = None 
            parent_linkFld: Any = None
            session_factory (sessionmaker[Session] | None, optional): Database session factory. Defaults to None.
            viewClass (Type[QTableView], optional): Table view class. Defaults to QTableView.
            parent (optional): Parent widget. Defaults to None.

        Raises:
            ValueError: If required parameters not provided.
        """

        if not self._ORMmodel:
            self.setORMmodel(ORMmodel)

        if not self._ssnmaker:
            self.setssnmaker(session_factory)

        ORMmdl = self.ORMmodel()
        ssnmkr = self.ssnmaker()
        if all([
            ORMmdl is not None,
            ssnmkr is not None,
            ]):
            super().__init__(model=ORMmdl, ssnmaker=ssnmkr, parent=parent)
        else:
            super(cSimpRecFmElement_Base, self).__init__(parent=parent)
        # endif for super() call

        if getattr(self, '_linkFld', None) is not None:
            # nothing to do - already set as class attribute
            pass
        else:
            if linkFld is not None:
                self._linkFld = getattr(self._ORMmodel, linkFld) if isinstance(linkFld, str) else linkFld # type: ignore
            # else:                
            #     raise ValueError("A linkFld must be provided either in the constructor or as a class attribute")
            # endif linkFld is not None
        # endif self._linkFld is not None

        if getattr(self, '_parent_linkFld', None) is not None:
            # nothing to do - already set as class attribute
            pass
        else:
            self._parent_linkFld = parent_linkFld
        # endif self._parent_linkFld is not None
        self.setParentLinkFromIncoming = self.parent_linkFld() is None      # if True, when loading from parent record, set parent link field to parent's PK

        self._recordList:list = []
        self._deleted_recordList:list = []

        self.layoutMain = QVBoxLayout(self)
        self.table = viewClass(parent=self)
        if ORMmdl is None:
            raise ValueError("ORMmodel must be provided")
        if ssnmkr is None:
            raise ValueError("session_factory must be provided")
        self.Tblmodel = SQLAlchemyTableModel(ORMmdl, ssnmkr, literal(False), parent=self)
        self.table.setModel(self.Tblmodel)
        self.layoutMain.addWidget(self.table)
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
    # get/set ORMmodel/primary_key

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

    def parent_linkFld(self):
        """Get the parent record primary key."""
        pRec = self.parentRec()
        linkFld = self._parent_linkFld
        if pRec:
            retval = getattr(pRec.__class__, linkFld) if isinstance(linkFld, str) else linkFld
        else:
            retval = linkFld
        return retval
    def parent_linkFld_keystr(self, rec):
        if rec is None:
            rec = self.parentRec()
        PLFkey = self.parent_linkFld()
        return str2(getattr(PLFkey, 'key', PLFkey))
    # get parent_linkFld, parent_linkFld_keystr

    def linkFld(self):
        """Get the parent foreign key field."""
        # return self._linkFld
        recKls = self.ORMmodel()
        lFld = self._linkFld
        if recKls:
            retval = getattr(recKls, lFld) if isinstance(lFld, str) else lFld
        else:
            retval = lFld
        return retval

    def setlinkFld(self, linkFld):
        """Set the parent foreign key field."""
        modl = self.ORMmodel()
        if not modl:
            raise ValueError("ORMmodel must be set before setting parentFK")
        self._linkFld = getattr(modl, linkFld) if isinstance(linkFld, str) else linkFld
    # get/set parentFK

    def parentRec(self):
        """Get the parent record."""
        return self._parentRec
    def setparentRec(self, rec):
        """Set the parent record and extract its primary key."""
        self._parentRec = rec
        if self.setParentLinkFromIncoming and rec is not None:
            self._parent_linkFld = get_primary_key_column(rec.__class__)
    # get/set parentFK


    # --- Lifecycle hooks ---
    def loadFromRecord(self, rec=None, *caller_conditions):
        """Load subrecords for the given parent record."""
        self.setparentRec(rec)
        self._recordList.clear()
        self._deleted_recordList.clear()

        # implement later - verify that caller_conditions are valid SQLAlchemy expressions
        # from sqlalchemy.sql.elements import ColumnElement

        for c in caller_conditions:
            if not isinstance(c, ColumnElement):
                raise TypeError(f"Invalid condition: {c!r}")
        conditions = list(caller_conditions)
        PLFkey = self.parent_linkFld_keystr(rec)
        if PLFkey and self.linkFld():
            conditions.append(self.linkFld() == PLFkey)

        ssnmkr = self.ssnmaker()
        assert ssnmkr is not None, "Sessionmaker must be set before touching the database"
        ORMmdl = self.ORMmodel()
        assert ORMmdl is not None, "ORMmodel must be set before loading records"
        with ssnmkr() as session:
            stmt = select(ORMmdl)
            if conditions:
                stmt = stmt.where(*conditions)
            rows = session.scalars(stmt).all()
            for r in rows:
                session.expunge(r)
            self._recordList.extend(rows)

            self.Tblmodel.refresh(filter=conditions)
        #endwith
    def loadRecords(self, *caller_conditions):
        """Load records - assumes no parent record """
        return self.loadFromRecord(None, *caller_conditions)
    # loadFromRecord

    def saveToRecord(self, rec = None):
        """Save subrecords back to database."""
        parntRec = self.parentRec()
        if parntRec != rec:
            raise ValueError("Parent record mismatch on saveToRecord")

        PLFkey = self.parent_linkFld_keystr(rec)

        ssnmkr = self.ssnmaker()
        assert ssnmkr is not None, "Sessionmaker must be set before touching the database"
        with ssnmkr() as session:
            # reattach new/edited
            for rec in self._recordList:
                if parntRec is not None:
                    setattr(rec, self.linkFld().key, getattr(parntRec, PLFkey)) # type: ignore
                session.merge(rec)

            # delete removed
            for rec in self._deleted_recordList:
                obj = session.merge(rec)
                session.delete(obj)

            session.commit()
        # endwith

        self._deleted_recordList.clear()
    # saveForParent
    def saveRecords(self):
        return self.saveToRecord()
        ...

    # --- Internal helpers ---

    def add_row(self):
        """Add a new empty row to the subform table."""
        row = self.ORMmodel()
        self._recordList.append(row)
        self.Tblmodel.insertRow(row)
    # add_row

    def del_row(self):
        """Delete the selected row(s) from the subform table."""
        idxs = self.table.selectionModel().selectedRows()
        for idx in sorted(idxs, key=lambda x: x.row(), reverse=True):
            rec = self.Tblmodel.record(idx.row())
            if rec in self._recordList:
                self._recordList.remove(rec)
                self._deleted_recordList.append(rec)
            self.Tblmodel.removeRow(idx.row())
        # end for
    # del_row
# cRFRecordGrid

class cSRFRecordList_Record(
    cSRF_Formdb_Base,
    cSRF_FormUI_Base,
    ):
    """
    A single record form to be used as the item widget in a cSRFRecordList. Inherits from both cSRF_Formdb_Base and cSimpRecFmElement_Base to provide both UI and db functionality.
    The UI functionality is provided by a simple form layout with field widgets.

    Args:
        rec (Any): ORM record to display.
        parent (QWidget | None, optional): Parent widget. Defaults to None.
    """

    def __init__(self, 
        rec = None,
        parent:QWidget|None=None,
        *args, **kwargs):
        

        if getattr(self, '_ORMmodel', None) is None:
            if rec is not None:
                self._ORMmodel = rec.__class__

        if getattr(self, '_ssnmaker', None) is None:
            self._ssnmaker = getattr(parent, '_ssnmaker', None)
            if not self._ssnmaker:
                raise ValueError(f"A sessionmaker must be provided defined in the parent form {parent}")

        super().__init__(model=self._ORMmodel, ssnmaker=self._ssnmaker, parent=parent)
        # did field defs get set by super().__init__()? if not, try to get from parent

        # initialdisplay(self):
        self.setcurrRec(rec)
        self.fillFormFromcurrRec()
        # self.showNewRecordFlag(self.isNewRecord())
    # __init__

    ######################################################
    ########    property and key widget getters/setters

    ######################################################
    ########    Layout construction

    def _buildFormLayout(self) -> cQFormLayout:
        """Build the layout for a subrecord form element.

        Returns:
            tuple: (layoutMain, layoutForm, layoutButtons) where layoutButtons is None.
        """


        layoutMain = QVBoxLayout(self)
        layoutForm = cGridWidget(scrollable=True)
        layoutFormFixedTop = QGridLayout()
        layoutFormPages = cstdTabWidget()
        layoutFormFixedBottom = QGridLayout()
        statusBar = QStatusBar(self)

        # should this be in _finalizeMainLayout instead?
        layoutForm.addLayout(layoutFormFixedTop, 0, 0)
        layoutForm.addWidget(layoutFormPages, 1, 0)
        layoutForm.addLayout(layoutFormFixedBottom, 2, 0)

        newrecFlag = QLabel("New Rec", self)
        fontNewRec = QFont()
        fontNewRec.setBold(True)
        fontNewRec.setPointSize(10)
        fontNewRec.setItalic(True)
        newrecFlag.setFont(fontNewRec)
        newrecFlag.setStyleSheet("color: red;")
        layoutMain.addWidget(newrecFlag) # at top for visibility - different from main form

        rtnobj: cQFormLayout = cQFormLayout(
            main=layoutMain,
            form=layoutForm,
            fixed_top=layoutFormFixedTop,
            pages=layoutFormPages,
            fixed_bottom=layoutFormFixedBottom,
            status_bar=statusBar,
            header=QHBoxLayout(),  # subforms don't have a header
            buttons=QHBoxLayout(), # subforms don't have action buttons
            
            lblFormName=None, # subforms don't have a form name label
            newrecFlag=newrecFlag,
        )
        return rtnobj
    # _buildFormLayout

    #############################################################
    ########    overrides of cSimpleRecordForm_Base methods
    #############################################################

    def _addActionButtons(self) -> None:
        return None

    ######################################################
    ########    Display 

    def fillFormFromcurrRec(self):
        """Load the current record into all form fields.

        Updates all field widgets with values from the current record
        and updates the dirty and new record flags.
        """
        for Wstruc in self._formWidgets.values():
            widg = Wstruc.widget
            if isinstance(widg, cSimpRecFmElement_Base):
                widg.loadFromRecord(self.currRec())

        self.showNewRecordFlag()
        self.showCommitButton()
        # self.setDirty(False) - nope, don't need to set form dirty state here - isDirty checks individual fields
    # fillFormFromRec

    # TODO: wrap with fillFormFromcurrRec
    # TODO: play with positioning of new record flag
    def showNewRecordFlag(self) -> None:
        """Show or hide the 'New Record' flag based on current record state."""
        nrf = getattr(self, '_newrecFlag', None)
        if not isinstance(nrf, QWidget):
            return
        nrf.setVisible(self.isNewRecord())

    def showCommitButton(self) -> None:
        """Show the commit button if the record is dirty."""
        btnCommit = getattr(self, 'btnCommit', None)
        if not isinstance(btnCommit, QWidget):
            return
        btnCommit.setEnabled(self.isDirty())
    # showCommitButton    

    ###########################################################
    ############ organize past this point
    ###########################################################
    
    def isNewRecord(self) -> bool:
        """Check if the current record is a new (unsaved) record.

        Returns:
            bool: True if the current record has no primary key value, False otherwise.
        """
        pKey = self.primary_key()
        currRec = self.currRec()
        return currRec is None or getattr(currRec, pKey.key) is None

    @Slot()
    def setDirty(self, dirty: bool|None = None):
        """Poll children for dirty state and update save button."""
        # removed code to set dirty state of children, since each adapter handles its own dirty state internally and the form's dirty state is determined by polling the children when needed

        # Enable save button if anything is dirty
        btnCommit = getattr(self, 'btnCommit', None)
        if hasattr(btnCommit, 'setEnabled'):
            btnCommit.setEnabled(self.isDirty()) # type: ignore
    # setFormDirty

    def isDirty(self) -> bool:
        """Check if any form element is dirty."""
        # any() stops and returns True as soon as it finds the first True
        return any(el.widget.isDirty() for el in self._formWidgets.values())       # type: ignore
    # isDirty


    
# cSRFRecordList_Record
class cSRFRecordList(cSRFSingleRecordForm):     # is cSRFSingleRecordForm = cSRF_Formdb_Base + cSRF_FormUI_Base the right parent?
    """
    Base class for record list subforms. Should be used as a subform within a cSRFMultiRecordWrapper. Inherits from both cSRF_FormUI_Base and cSRF_Formdb_Base to provide both UI and db functionality.
    The UI functionality is provided by a QListWidget.

        Args:
            rec (Any): ORM record to display.
            parent (QWidget | None, optional): Parent widget. Defaults to None.

    """

    def __init__(self, 
        ORMmodel: Type[Any]|None = None,
        linkFld: Any = None,
        parent_linkFld: Any = None,
        session_factory: sessionmaker[Session] | None = None,
        viewClass: Type[QListWidget] = QListWidget,
        parent:QWidget|None=None,
        *args, **kwargs):
        
        self.vwClass = viewClass
        super().__init__(model=ORMmodel, ssnmaker=session_factory, parent=parent)
        
        if not self._ORMmodel:
            if not ORMmodel:
                raise ValueError("A model class must be provided either in the constructor or as a class attribute")
            self._ORMmodel = ORMmodel
        self._primary_key = get_primary_key_column(self._ORMmodel)

        if getattr(self, '_linkFld', None) is not None:
            # nothing to do - already set as class attribute
            pass
        else:
            if linkFld is not None:
                self._linkFld = getattr(self._ORMmodel, linkFld) if isinstance(linkFld, str) else linkFld # type: ignore
            # else:                
            #     raise ValueError("A linkFld must be provided either in the constructor or as a class attribute")
            # endif linkFld is not None
        # endif self._linkFld is not None

        if getattr(self, '_parent_linkFld', None) is not None:
            # nothing to do - already set as class attribute
            pass
        else:
            self._parent_linkFld = parent_linkFld # type: ignore
        # endif self._parent_linkFld is not None
        # if setParentLinkFromIncoming, when loading from parent record, set parent link field to parent's PK
        self.setParentLinkFromIncoming = self._parent_linkFld is None   # if parent_linkFld provided in constructor, only set from incoming if it's None

        self._ssnmaker = getattr(parent, '_ssnmaker', None)
        if not self._ssnmaker:
            raise ValueError(f"A sessionmaker must be provided defined in the parent form {parent}")

        self.OLDfieldDefs = getattr(parent, 'fieldDefs', {})

        self._parentRec = None  # set by parent form when loading
        self._childRecs:list = []
        self._deleted_childRecs:list = []

    # __init__

    ######################################################
    ########    property and key widget getters/setters

    def linkFld(self):
        """Get the parent foreign key field."""
        # return self._linkFld
        recKls = self.ORMmodel()
        lFld = self._linkFld
        if recKls:
            retval = getattr(recKls, lFld) if isinstance(lFld, str) else lFld
        else:
            retval = lFld
        return retval
    def setlinkFld(self, linkFld):
        """Set the parent foreign key field."""
        modl = self.ORMmodel()
        if not modl:
            raise ValueError("ORMmodel must be set before setting parentFK")
        self._linkFld = getattr(modl, linkFld) if isinstance(linkFld, str) else linkFld
    # get/set linkFld

    def parentRec(self):
        """Get the parent record."""
        return self._parentRec
    def setparentRec(self, rec):
        """Set the parent record and extract its primary key."""
        self._parentRec = rec
        if self.setParentLinkFromIncoming and rec is not None:
            self._parent_linkFld = get_primary_key_column(rec.__class__)
    def parent_linkFld(self):
        """Get the parent record primary key."""
        pRec = self.parentRec()
        linkFld = self._parent_linkFld
        if pRec:
            retval = getattr(pRec.__class__, linkFld) if isinstance(linkFld, str) else linkFld
        else:
            retval = linkFld
        return retval
    def parent_linkFld_keystr(self, rec = None):
        if rec is None:
            rec = self.parentRec()
        PLFkey = self.parent_linkFld()
        return str2(getattr(PLFkey, 'key', PLFkey))
    # get/set parentFK

    ######################################################
    ########    Layout construction

    def _buildFormLayout(self) -> cQFormLayout:
        """Build the layout for a subrecord form element.

        Returns:
            tuple: (layoutMain, layoutForm, layoutButtons) where layoutButtons is None.
        """
        
        layoutMain = QVBoxLayout(self)
        layoutForm = cGridWidget(scrollable=True)
        layoutFormFixedTop = QGridLayout()
        layoutFormPages = cstdTabWidget()
        layoutFormFixedBottom = QGridLayout()
        layoutButtons = QHBoxLayout()  # subforms don't have action buttons, but create layout for consistency and potential future use
        statusBar = QStatusBar(self)

        # should this be in _finalizeMainLayout instead?
        layoutForm.addLayout(layoutFormFixedTop, 0, 0)
        layoutForm.addWidget(layoutFormPages, 1, 0)
        layoutForm.addLayout(layoutFormFixedBottom, 2, 0)

        newrecFlag = QLabel()

        #TODO: add dispArea via fieldDef and allow it to be customized by passing a viewClass in the constructor or as a class attribute, defaulting to QListWidget for cSRFRecordList and QTableView for cSRFRecordGrid. This will also allow multiple different views for the same or even diffferent data if desired.
        viewClass = self.vwClass if hasattr(self, 'vwClass') else QListWidget
        self.dispArea = viewClass(parent=self)
        layoutFormPages.addTab(self.dispArea, '')

        # put it all together
        layoutMain.addWidget(layoutForm)
        layoutMain.addLayout(layoutButtons)
        layoutMain.addWidget(statusBar)

        rtnobj: cQFormLayout = cQFormLayout(
            main=layoutMain,
            form=layoutForm,
            fixed_top=layoutFormFixedTop,
            pages=layoutFormPages,
            fixed_bottom=layoutFormFixedBottom,
            status_bar=statusBar,
            header=QHBoxLayout(),  # subforms don't have a header
            buttons=layoutButtons, # subforms don't have action buttons
            
            lblFormName=None, # subforms don't have a form name label
            newrecFlag=newrecFlag,
        )
        return rtnobj
    # _buildFormLayout

    def _buildPages(self) -> None:
        """Build pages (not used for list-based subforms - single page only)."""
        # nope, just the one page
        # do I need to construct the page?
        # TODO: if we want to support multiple pages in a list-based subform, we'll need to implement this method to create and manage the additional pages, and also update the fieldDefs to specify which fields go on which pages. For now, just return since we're only using a single page.
        #       also see note on self.dispArea in _buildFormLayout - if we want to support multiple pages, we'll need to manage multiple view widgets as well and update self.dispArea to point to the currently active page's view widget.
        return
    # _buildPages

    
    ######################################################
    ########    field and Widget placement

    def defineActionButtons(self):
        """Define action buttons for the subform."""
        return [
            cQFormBtnDef(text="Add", action=self.add_row),
            cQFormBtnDef(text="Delete", action=self.del_row),
        ]
    # defineActionButtons
    
    ######################################################
    ########    Display 

    def initialdisplay(self):
        """Initialize display (no-op for subrecord forms since record is passed in constructor)."""
        # this is a noop here since record is passed in constructor
        return
    # initialdisplay()

    def _addDisplayRow(self, rec):
        """Add a display row for the given record."""
        # does NOT add to _childRecs - that must be done separately (document why)
        wdgt = cSRFRecordList_Record(rec, parent=self)
        QLWitm = QListWidgetItem()
        QLWitm.setSizeHint(wdgt.sizeHint())
        self.dispArea.addItem(QLWitm)
        self.dispArea.setItemWidget(QLWitm, wdgt)
    # _addDisplayRow


    ##########################################
    ########    Create

    def add_row(self):
        """Add a new subrecord row to the list."""
        modl = self.ORMmodel()
        assert modl is not None, "ORMmodel must be set before adding a row"
        row = modl()
        linkFld = self.linkFld()
        if self.parentRec() is not None:
            setattr(row, linkFld.key, getattr(self.parentRec(), self.parent_linkFld_keystr(), None)) # type: ignore

        self._childRecs.append(row)
        self._addDisplayRow(row)
    # add_row


    ##########################################
    ########    Read

    def loadFromRecord(self, rec, *caller_conditions):
        """Load subrecords for a parent record, or all records when parent is None."""
        self.setparentRec(rec)
        self._childRecs.clear()
        self._deleted_childRecs.clear()

        ssnmkr = self.ssnmaker()
        assert ssnmkr is not None, "Sessionmaker must be set before touching the database"
        modl = self.ORMmodel()
        assert modl is not None, "ORMmodel must be set before loading records"
        linkFld = self.linkFld()
        parnt_linkFldKey = self.parent_linkFld_keystr(rec)

        # for c in caller_conditions:
        #     if not isinstance(c, ColumnElement):
        #         raise TypeError(f"Invalid condition: {c!r}")
        conditions = list(caller_conditions)
        if rec is not None:
            conditions.append(linkFld == getattr(rec, parnt_linkFldKey))

        with ssnmkr() as session:
            qry = select(modl)
            if conditions:
                qry = qry.where(*conditions)
            rows = session.scalars(qry).all()
            for r in rows:
                session.expunge(r)
            self._childRecs.extend(rows)
        #endwith

        # clear _recDisplArea and repopulate from _childRecs
        self.dispArea.clear()
        for rec in self._childRecs:
            self._addDisplayRow(rec)
        # endfor rec in self._childRecs

        # self.Tblmodel.refresh(filter=(self._parentFK == getattr(rec, self._parentRecPK.key)))
    def loadRecords(self, *caller_conditions):
        return self.loadFromRecord(None, *caller_conditions)
    # loadFromRecord


    ##########################################
    ########    Update

    def saveToRecord(self, rec):
        """Save subrecords back to database.

        If a parent record context is active, each child record's link field is
        updated from the parent key before merge. Without a parent context,
        records are persisted as-is.
        """
        pRec = self.parentRec()
        if pRec != rec:
            raise ValueError("Parent record mismatch on saveToRecord")

        ssnmkr = self.ssnmaker()
        assert ssnmkr is not None, "Sessionmaker must be set before touching the database"
        modl = self.ORMmodel()
        assert modl is not None, "ORMmodel must be set before saving record"
        linkFld = self.linkFld()
        with ssnmkr() as session:
            # reattach new/edited
            for rec in self._childRecs:
                if pRec is not None:
                    setattr(rec, linkFld.key, getattr(pRec, self.parent_linkFld_keystr())) # type: ignore
                session.merge(rec)

            # delete removed
            for rec in self._deleted_childRecs:
                if pRec is None or getattr(rec, self.primary_key().key, None) is not None:
                    obj = session.merge(rec)
                    session.delete(obj)

            session.commit()
        # endwith

        self._deleted_childRecs.clear()

        self.loadFromRecord(pRec)   # reload to refresh display area
    # saveForParent



    ##########################################
    ########    Delete

    #TODO: implement del_row
    def del_row(self):
        """Delete selected subrecord rows (not yet fully implemented)."""
        idxs = self.dispArea.selectionModel().selectedRows()    # does dispArea have selectionModel()?
        # for idx in sorted(idxs, key=lambda x: x.row(), reverse=True):
        #     rec = self.Tblmodel.record(idx.row())
        #     if rec in self._childRecs:
        #         self._childRecs.remove(rec)
        #         self._deleted_childRecs.append(rec)
            # see loadFromRecord for how to add to display area
            # self.Tblmodel.removeRow(idx.row())
    # del_row



    ##########################################
    ########    Record Status

    # cSimpleRecordForm_Base already has this covered


# other form classes can be added here as needed, following the same pattern of inheriting from the appropriate base classes to combine UI and db functionality as needed.
# Note that a cSRFRecordGridForm = cSRFMultiRecordWrapper + cSRFRecordGrid is not necessary, as the cSRFRecordGrid can simply be used as a subform within the cSRFMultiRecordWrapper, and the cSRFMultiRecordWrapper can be used on its own as a wrapper for any number of subforms, including cSRFRecordGrids and cSRFRecordLists.
# similarly, a cSRFRecordListForm = cSRFMultiRecordWrapper + cSRFRecordList is not necessary, as the cSRFRecordList can simply be used as a subform within the cSRFMultiRecordWrapper, and the cSRFMultiRecordWrapper can be used on its own as a wrapper for any number of subforms, including cSRFRecordGrids and cSRFRecordLists.

class cSRFRecordGridForm(cSRFMultiRecordWrapper):
    ...

class cSRFRecordListForm(cSRFMultiRecordWrapper):
    ...

