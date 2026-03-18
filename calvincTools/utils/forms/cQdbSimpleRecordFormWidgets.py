from PySide6.QtGui import QFont, QIcon
import qtawesome

from calvincTools.utils.SQLAlcTools import get_primary_key_column
from calvincTools.utils.cQWidgets import cComboBoxFromDict, cDataList, cGridWidget, cstdTabWidget
from calvincTools.utils.forms.cQFormWidgets import cQFmConstants, cQFmNameLabel
from calvincTools.utils.forms.cQdbFormWidgets import cQFmFldWidg, cQFmLookupWidg, cSimpRecFmElement_Base
from calvincTools.utils.messageBoxes import areYouSure

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QBoxLayout, QGridLayout, QHBoxLayout, QLabel, QLayout, QLineEdit, QMessageBox, QPushButton, QStatusBar, QTabWidget, QVBoxLayout, QWidget
from sqlalchemy import func
from sqlalchemy.orm import Session, sessionmaker

from typing import Any, Dict, List, Type


# TODO: Handle fields that need special massaging   - let the children do the heavy lifting ??
# TODO: pretty up NEW RECORD FLAG
class cSimpleRecordForm_Base(QWidget):
    """Base class for simple record forms with CRUD operations.

    This abstract base class provides the foundation for creating database-backed
    forms with navigation, editing, and persistence capabilities. It manages
    form fields, handles dirty state tracking, and provides standard CRUD operations.

    Attributes:
        _ORMmodel (Type[Any] | None): The SQLAlchemy ORM model class.
        _primary_key: Primary key column of the ORM model.
        _currRec: Currently loaded ORM record.
        _ssnmaker (sessionmaker[Session] | None): Database session factory.
        pages (List): List of page/tab names for multi-page forms.
        fieldDefs (Dict[str, Dict[str, Any]]): Field definitions for the form.
    """
    # TODO: be more careful with class attributes vs instance attributes
    _ORMmodel:Type[Any]|None = None
    _primary_key: Any
    _currRec: Any

    _ssnmaker:sessionmaker[Session]|None = None

    pages: List = []
    _tabindexTOtabname: dict[int, str] = {}
    _tabnameTOtabindex: dict[str, int] = {}
    fieldDefs: Dict[str, Dict[str, Any]] = {}

    def __init__(self,
        model: Type[Any]|None = None,
        ssnmaker: sessionmaker[Session] | None = None,

        parent: QWidget | None = None
        ):
        """Initialize the base record form.

        Args:
            model (Type[Any] | None, optional): ORM model class. Defaults to None.
            ssnmaker (sessionmaker[Session] | None, optional): Session factory. Defaults to None.
            parent (QWidget | None, optional): Parent widget. Defaults to None.

        Raises:
            ValueError: If model or ssnmaker not provided and not set as class attributes.
        """
        # super init
        super().__init__(parent)

        self._formWidgets: Dict[str, QWidget] = {}
        self._lookupFrmElements: Dict[str, QWidget] = {}

        # set model, primary key
        if not self._ORMmodel:
            if not model:
                raise ValueError("A model class must be provided either in the constructor or as a class attribute")
            self.setORMmodel(model)
        self.setPrimary_key()

        # set ssnmaker
        if not self._ssnmaker:
            if not ssnmaker:
                raise ValueError("A sessionmaker must be provided either in the constructor or as a class attribute")
            self.setssnmaker(ssnmaker)

        dictFormLayouts = self._buildFormLayout()
        assert isinstance(dictFormLayouts, dict), "_buildFormLayout must return a dict of layouts"
        self.dictFormLayouts = dictFormLayouts
        layoutMain = dictFormLayouts.get('layoutMain')
        assert isinstance(layoutMain, (QVBoxLayout, )), "layoutMain must be a QVBoxLayout"
        layoutFormHdr = dictFormLayouts.get('layoutFormHdr')
        # assert isinstance(layoutFormHdr, (QGridLayout, )), "layoutFormHdr must be a QGridLayout"
        layoutForm = dictFormLayouts.get('layoutForm')
        # assert isinstance(layoutForm, QTabWidget), "layoutForm must be a QTabWidget"
        self.layoutFormFixedTop = dictFormLayouts.get('layoutFormFixedTop')
        if self.layoutFormFixedTop is not None:
            assert isinstance(self.layoutFormFixedTop, QGridLayout), "layoutFormFixedTop must be a QGridLayout"
        self.layoutFormPages = dictFormLayouts.get('layoutFormPages')
        assert isinstance(self.layoutFormPages, QTabWidget), "layoutFormPages must be a QTabWidget"
        self.layoutFormFixedBottom = dictFormLayouts.get('layoutFormFixedBottom')
        if self.layoutFormFixedBottom is not None:
            assert isinstance(self.layoutFormFixedBottom, QGridLayout), "layoutFormFixedBottom must be a QGridLayout"
        self.layoutButtons = dictFormLayouts.get('layoutButtons')
        assert isinstance(self.layoutButtons, (QHBoxLayout, QVBoxLayout)), "layoutButtons must be a QHBoxLayout or QVBoxLayout"
        # rtnDict['statusBar'] = statusBar
        self._statusBar = dictFormLayouts.get('statusBar')
        if self._statusBar is not None:
            assert isinstance(self._statusBar, QStatusBar), "statusBar must be a QStatusBar"
        # rtnDict['lblFormName'] = lblFormName
        # rtnDict['newrecFlag'] = newrecFlag
        self._newrecFlag = self.dictFormLayouts.get('newrecFlag')

        self._buildPages(self.layoutFormPages)

        # Let subclass build its widgets into self.layoutForm
        self._placeFields(self.layoutFormPages, self.layoutFormFixedTop, self.layoutFormFixedBottom)

        # Add buttons
        self._addActionButtons(self.layoutButtons)

        # Finalize layout
        self._finalizeMainLayout(
            layoutMain=layoutMain,
            items=[
                layoutFormHdr,
                layoutForm,
                self.layoutButtons,
                self._statusBar
            ]
        )

        self.initialdisplay()

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
        return self._currRec

    def setcurrRec(self, rec):
        """Set the current record.

        Args:
            rec: ORM record object to set as current.
        """
        self._currRec = rec
    # get/set currRec

    ######################################################
    ########    Layout and field and Widget placement

    def _buildFormLayout(self) -> Dict[str, QWidget|QLayout|None]:
        """
        Build the main layout, form layout, and button layout. Must be implemented by subclasses.
        Creates and configures:
        1. layoutMain: the main layout for the form (QVBoxLayout or QHBoxLayout)
        2. layoutForm: the grid layout for the form fields  (QTabWidget)
        3. layoutButtons: the layout for the action buttons (QHBoxLayout or QVBoxLayout)

        Form elements created here, but not returned:
        4. _statusBar: the status bar for the form (QStatusBar)
        5. _newrecFlag: the "New Record" flag label (QLabel)
        6. layoutFormHdr: the header layout for the form (QHBoxLayout)
        7. lblFormName: the form name label (cQFmNameLabel)
        8. Set the window title to the form name

        Returns:
            tuple (layoutMain:QBoxLayout, layoutForm:QTabWidget, layoutButtons:QBoxLayout|None)

        """
        raise NotImplementedError

        ## see cSimpRecForm for an example implementation
        ##

    # _buildFormLayout

    def _buildPages(self, layoutFormPages: QTabWidget) -> None:
        """Build the pages (tabs) for the form based on self.pages."""
        if self.numPages() < 1:
            # single page form
            self.pages = ['Main']
            self._tabindexTOtabname[0] = 'Main'
            self._tabnameTOtabindex['Main'] = 0
        # endif numPages

        for n, pg in enumerate(self.pages):
            pgnm = str(pg)
            self._tabindexTOtabname[n] = pg
            self._tabnameTOtabindex[pg] = n

            widg, grid = QWidget(), QGridLayout()
            widg.setLayout(grid)
            layoutFormPages.addTab(widg, self.tr(pgnm))
        # endfor enum pages
    # _buildPages
    def FormPage(self, idx:int|str) -> QGridLayout|None:
        """Return the QGridLayout for the given page index or name."""
        if isinstance(idx, str):
            tabidx = self._tabnameTOtabindex.get(idx)
            if tabidx is None:
                return None
        else:
            tabidx = idx
        #endif idx type

        # is idx one of the special values?
        if tabidx == cQFmConstants.pageFixedTop.value:
            return self.layoutFormFixedTop if isinstance(self.layoutFormFixedTop, QGridLayout) else None
        elif tabidx == cQFmConstants.pageFixedBottom.value:
            return self.layoutFormFixedBottom if isinstance(self.layoutFormFixedBottom, QGridLayout) else None
        # endif special values

        assert isinstance(self.layoutFormPages, QTabWidget), "layoutFormPages must be a QTabWidget"
        widg = self.layoutFormPages.widget(tabidx)
        if widg is None:
            return None
        L = widg.layout()
        return L if isinstance(L, QGridLayout) else None
    # FormPage
    def numPages(self) -> int:
        """Return the number of pages/tabs in the form.

        Returns:
            int: Number of pages.
        """
        return len(self.pages)
        # or return self.layoutForm.count() # mebbe not - see _buildPages
    # numPages

    def _placeFields(self, layoutFormPages:QTabWidget, layoutFormFixedTop: QGridLayout|None, layoutFormFixedBottom: QGridLayout|None, lookupsAllowed: bool = True) -> None:
        """
        Build widgets and wrap them into _cSimpRecFmElmnt_Base adapters.
        Args:
            lookupsAllowed (bool, optional): Whether to create lookup widgets for fields prefixed with '@'. Defaults to True.
        """

        def _apply_optional_attrib(widget, attr, value):
            """
            helper function for setting optional attributes

            Args:
                widget (_type_): _description_
                attr (_type_): _description_
                value (_type_): _description_
            """
            if value is None: return
            if hasattr(widget, attr):
                getattr(widget, attr)(value)
            else:
                widget.setProperty(attr, value)
        # _apply_opt_attr

        ssnmkr = self.ssnmaker()
        assert ssnmkr is not None, "ssnmkr must be set before placing fields"
        # ssnmkr = ssnmkr if ssnmkr else get_app_sessionmaker()
        mdl = self.ORMmodel()
        assert mdl is not None, "ORMmodel must be set before placing fields"

        for fldNameKey, fldDef in self.fieldDefs.items():
            widget = None

            # fldNameKey indicates a lookup field if the field name starts with '@'
            # lookup will be the boolean flag
            # fldName is the actual field name
            isLookup = (fldNameKey.startswith(cQFmConstants.flagLookupField.value))
            isInternalVarField = (fldNameKey.startswith(cQFmConstants.flagInternalVarField.value))
            fldName = fldNameKey if not isLookup else fldNameKey[1:]      # TODO: offset by length of flagLookupField instead of constant 1

            SubFormCls = fldDef.get("subform_class", None)
            isSubFormElmnt = (SubFormCls is not None)

            lookupHandler = fldDef.get('lookupHandler', None)
            lblText = fldDef.get('label', fldName)
            widgType = fldDef.get('widgetType', QLineEdit)
            alignlblText = fldDef.get('align', Qt.AlignmentFlag.AlignLeft)
            choices = fldDef.get('choices', None)
            initval = fldDef.get('initval', '')
            lblChkBxYesNo = fldDef.get('lblChkBxYesNo', None)
            focusPolicy = fldDef.get('focusPolicy', Qt.FocusPolicy.ClickFocus if (isLookup or isSubFormElmnt) else None)
            modlFld = fldName
            fmPg_indef = fldDef.get('page', 0)
            fmPg = fmPg_indef if isinstance(fmPg_indef, int) else self._tabnameTOtabindex.get(fmPg_indef, 0)
            pos = fldDef.get('position', None)

            # --- Subform case ---
            if isSubFormElmnt:
                widget = SubFormCls(session_factory=ssnmkr, parent=self)
                if not isinstance(widget, cSimpRecFmElement_Base):
                    raise TypeError(f'class {SubFormCls.__name__} must inherit from cSimpRecFmElement_Base')
            # --- Scalar case ---
            elif isLookup:
                if lookupsAllowed:
                    if widgType not in (cDataList, cComboBoxFromDict):
                        widgType = cDataList  # force it to be a cDataList
                    widget = cQFmLookupWidg(
                        session_factory=ssnmkr,
                        model=mdl,
                        lookup_field=modlFld,
                        lblText=lblText,
                        alignlblText=alignlblText,
                        lookupWidgType=widgType,
                        choices=choices,
                        parent=self
                    )
                    if lookupHandler:
                        if isinstance(lookupHandler, str):
                            if not hasattr(self, lookupHandler):
                                raise AttributeError(f"lookupHandler method '{lookupHandler}' not found in {self.__class__.__name__}")
                            lookupHandler = getattr(self, lookupHandler)
                        if not callable(lookupHandler):
                            raise TypeError("lookupHandler must be a callable function or a string name of a method")
                        widget.signalLookupSelected.connect(lookupHandler)
                    self._lookupFrmElements[fldNameKey] = widget
                    # endif lookupHandler
                # endif lookupsAllowed
            else:
                widget = cQFmFldWidg(
                    widgType=widgType,
                    lblText=lblText,
                    lblChkBxYesNo=lblChkBxYesNo,
                    alignlblText=alignlblText,
                    modlFld=modlFld,
                    choices=choices,
                    initval=initval,
                    parent=self
                )
            #endif subform vs scalar
            if widget is None:
                raise ValueError(f"Failed to create widget for field '{fldName}'")
            if focusPolicy:
                widget.setFocusPolicy(focusPolicy)

            if isinstance(widget, (cQFmFldWidg, cQFmLookupWidg)):
                # TODO: convert this to use _apply_opt_attr
                # optional field attributes
                W = widget._wdgt
                optAttributes = [
                    ('noedit', 'setProperty', W.setProperty),                                                                   # type: ignore
                    ('readonly', 'setReadOnly', W.setReadOnly if hasattr(W, 'setReadOnly') else W.setProperty),                 # type: ignore
                    ('frame', 'setFrame', W.setFrame if hasattr(W, 'setFrame') else W.setProperty),                             # type: ignore
                    ('maximumWidth', 'setMaximumWidth', W.setMaximumWidth if hasattr(W, 'setMaximumWidth') else W.setProperty), # type: ignore
                    ('focusPolicy', 'setFocusPolicy', W.setFocusPolicy if hasattr(W, 'setFocusPolicy') else W.setProperty),     # type: ignore
                    ('tooltip', 'setToolTip', W.setToolTip if hasattr(W, 'setToolTip') else W.setProperty),                     # type: ignore
                ]
                for attr, method_name, method in optAttributes:
                    attrVal = fldDef.get(attr, None)
                    if method_name == 'setProperty' or method is W.setProperty:
                        W.setProperty(attr, attrVal) if attrVal is not None else None
                    elif attrVal is not None:
                        method(attrVal) if hasattr(W, method_name) else W.setProperty(attr, attrVal) # type: ignore
                    #endif attrVal
                #endfor attr, method_name, method in optAttributes

                # other optional attributes
                attrVal = fldDef.get('bgColor', None)
                if attrVal is not None:
                    W.setStyleSheet(f"background-color: {attrVal};") if hasattr(W, 'setStyleSheet') else W.setProperty('bgColor', attrVal) # type: ignore
            #endif isinstance(widget, (cQFmFldWidg, cQFmLookupWidg)):

            # Register field and connect to changeField
            self.fieldDefs[fldNameKey]['widget'] = widget
            if not isLookup:  # or isInternalVarField ??
                self._formWidgets[fldNameKey] = widget

            # remove - this was done in the constructor
            # if isinstance(widget, cQFmFldWidg) and not isLookup and not isSubFormElmnt:
            #     widget.setModelField(fldName)

            if isinstance(widget, cQFmFldWidg):
                widget.signalFldChanged.connect(lambda *_, w=widget: self.changeFieldSlot(w))
            elif isinstance(widget, cQFmLookupWidg):
                widget.signalLookupSelected.connect(lambda *_, w=widget: self.changeFieldSlot(w))
            #endif isinstance(widget)

            # Place in layout
            if isinstance(pos, tuple) and len(pos) >= 2:
                fmLayout = self.FormPage(fmPg)
                if fmLayout is None:
                    raise ValueError(f"Form page {fmPg_indef} not found for field '{fldName}'")
                fmLayout.addWidget(widget, *pos)

        # endfor fldDef in self.fieldDefs
    # _placeFields

    # def _addActionButtons(self, layoutButtons:QBoxLayout|None = None) -> None:
    def _addActionButtons(self, layoutButtons:QBoxLayout|None) -> None:
        """Add action buttons to the form.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError
    # _addActionButtons

    def _handleActionButton(self, action: str) -> None:
        """Handle action button clicks.

        Args:
            action (str): Action name (e.g., 'save', 'delete').

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError
    # _handleActionButton

    def _finalizeMainLayout(self, layoutMain:QVBoxLayout, items:List|tuple) -> None:
        """Add all sub-layouts to the main layout in the correct order."""
        assert isinstance(layoutMain, QBoxLayout), 'layoutMain must be a Box Layout'

        for itm in items:
            if itm is None:
                continue
            elif isinstance(itm, QLayout):
                layoutMain.addLayout(itm)
            elif isinstance(itm, QWidget):
                layoutMain.addWidget(itm)
            elif isinstance(itm, (tuple, list)):
                L = QVBoxLayout()
                self._finalizeMainLayout(L, itm)
                layoutMain.addLayout(L)
            else:
                raise TypeError('items must be QLayout, QWidget, or tuple/list of these')
            # endif itm
        # endfor itm in items

        # self.setLayout(layoutMain)

    # _finalizeMainLayout

    ######################################################
    ########    Display 

    def initialdisplay(self):
        """Initialize and display the first record.

        Initializes a new record and loads the first record from the database.
        """
        self.initializeRec()
        self.on_loadfirst_clicked()
    # initialdisplay()

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

    def fillFormFromcurrRec(self):
        """Load the current record into all form fields.

        Updates all field widgets with values from the current record
        and updates the dirty and new record flags.
        """
        for widg in self._formWidgets.values():
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

    def repopLookups(self) -> None:
        """Repopulate all lookup widgets (e.g., after a save).

        Note:
            Currently not implemented.
        """
        return
        for lookupWidget in self._lookupFrmElements.values():
            lookupWidget.repopulateChoices()

    ##################################################
    ########    Navigation 

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
    def changeFieldSlot(self, widget: QWidget | None = None):
        # sender() returns the widget that triggered the signal
        if isinstance(widget, cQFmFldWidg):
            self.changeField(widget, widget.modelField(), widget.Value())
        if isinstance(widget, cQFmLookupWidg):
            self.changeField(widget, widget._lookup_field, widget.Value())
    def changeField(self, wdgt, dbField, wdgt_value, force=False):
        """
        Called when a widget changes.
        This no longer writes directly into the ORM object — adapters own that.
        Neither does it Marks the widget/adapter dirty
        Instead, it:
          - Applies optional transforms
          - Updates form-level dirty flag
        """
        # I don't wanna change the code below, which refers to 'widget'
        widget = wdgt

        if isinstance(widget, cQFmFldWidg) and widget.isInternalVarField():
            self.changeInternalVarField(widget, dbField, wdgt_value)
            # raise NotImplementedError("Internal variable fields not yet supported in changeField")

        # Ignore if noedit
        if getattr(widget, "property", lambda x: False)("noedit"):
            return

        # Apply transformation hook if subclass defines one
        transform_func = getattr(self, f"_transform_{dbField}", None)
        if callable(transform_func):
            wdgt_value = transform_func(wdgt_value)

        # Update form dirty state
        # self.setDirty(widget, True)  # doesn't the widget itself do this?
        self.showCommitButton()
        # endif wdgt_value
    # changeField

    def changeInternalVarField(self, wdgt, intVarField, wdgt_value):
    # def changeInternalVarField(self, wdgt):
        """
        Called when an internal variable field widget changes.
        Updates the internal variable field value.

        Args:
            wdgt: The widget that changed.
            intVarField: The internal variable field name.
            wdgt_value: The new value from the widget.
            force (bool, optional): Whether to force the change even if the value is the same. Defaults to False.
        """

        # to be implemented by subclass if needed
        raise NotImplementedError("changeInternalVarField not implemented")

        # # Ignore if noedit
        # if getattr(wdgt, "property", lambda x: False)("noedit"):
        #     return

        # current_value = getattr(self, intVarField, None)
        # if current_value == wdgt_value:
        #     return  # No change

        # setattr(self, intVarField, wdgt_value)

    # changeInternalVarField

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
            for fldName, fldDef in self.fieldDefs.items():
                isSubFormElmnt = "subform_class" in fldDef
                if not isSubFormElmnt:      # subforms handled after main record is saved
                    widget = self._formWidgets.get(fldName)
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
            for fldName, fldDef in self.fieldDefs.items():
                isSubFormElmnt = "subform_class" in fldDef
                if isSubFormElmnt:
                    widget = self._formWidgets.get(fldName)
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
        # rethink - adapters handle their own dirty state
        # so all that needs to be set here is self.dirty
        # right?

        # better yet, self doesn't need to track its dirty state
        # since  isDirty will poll children

        # keep an eye on the time the polling takes
        # if it's excessive, find the best way to record child dirty states

        # is this really the right way to handle this?
        if isinstance(dirty, bool):
            for el in self._formWidgets.values():
                if isinstance(el, cSimpRecFmElement_Base):
                    el.setDirty(dirty)

        # Enable save button if anything is dirty
        btnCommit = getattr(self, 'btnCommit', None)
        if hasattr(btnCommit, 'setEnabled'):
            btnCommit.setEnabled(self.isDirty()) # type: ignore
    # setFormDirty

    # the old code
    # def isDirty(self, widg = None) -> bool:
    #     """Check if any form element is dirty.

    #     Returns:
    #         bool: True if any child element has been modified, False otherwise.
    #     """
    #     target_widget = widg if widg is not None else self
    #     if not hasattr(target_widget, '_formWidgets'):
    #         return False

    #     # poll cQFmWidget children; if one is Dirty, form is Dirty
    #     for FmElement in target_widget._formWidgets.values():
    #         if not isinstance(FmElement, cSimpRecFmElement_Base):
    #             if self.isDirty(FmElement):
    #                 return True
    #         elif FmElement.isDirty():
    #             return True
    #     #endfor FmElement in self.children():

    #     return False
    # I'm rewriting isDirty to use any() and a generator expression
    def isDirty(self) -> bool:
        """Check if any form element is dirty."""
        # any() stops and returns True as soon as it finds the first True
        return any(el.isDirty() for el in self._formWidgets.values())       # type: ignore
# cSimpleRecordForm_Base


class cSimpleRecordForm(cSimpleRecordForm_Base):
    """A concrete implementation of cSimpleRecordForm_Base with standard layout.

    This class provides a complete single-record form with navigation buttons,
    CRUD operations, and a tabbed interface for organizing fields across multiple pages.

    Attributes:
        _formname: Name/title of the form.
    """
    """
    UPDATE THIS DOCUMENTATION!! UPDATE ME!!
    A simple record form for editing database records.

    Args:
        rec (SQLAlchemy Model Class Instance): The record to edit.
        formname (str | None, optional): The name of the form. Defaults to None.
        parent (QWidget | None, optional): The parent widget. Defaults to None.

    Properties and Methods implemented by child classes:
        _buildForm(self) -> None: where the subclass lays out its widgets.
        changeField(self, fld: cQFmFldWidg) -> None: what to do when a field changes.
        bindField(self, fld: cQFmFldWidg, get_value: Callable[[], Any], set_value: Callable[[Any], None]) -> None: bind a field to a record attribute.
        loadRecord(self) -> None: load the current record into the form fields.
        saveRecord(self) -> None: save the form field values back to the current record.

    Properties:
        formFields (dict[str, cQFmFldWidg]): The form fields in the record.
        currRec (Any): The current record being edited.

    Methods:
        getValue(self, fld: cQFmFldWidg) -> Any: Get the value of a form field.
        setValue(self, fld: cQFmFldWidg, value: Any) -> None: Set the value of a form field.

    Returns:
        _type_: _description_
    """

    def __init__(self,
        model: Type[Any]|None = None,
        formname: str|None = None,
        ssnmaker: sessionmaker[Session] | None = None,
        parent: QWidget | None = None
        ):
        """
        Initialize the form with a record and optional name.

        Args:
            rec (SQLAlchemy Model Class Instance): The record to edit.
            formname (str | None, optional): The name of the form. Defaults to None.
            parent (QWidget | None, optional): The parent widget. Defaults to None.
        """
        self._formname = getattr(self, '_formname', None)
        if not self._formname:
            self._formname = formname if formname else 'Form'

        super().__init__(model=model, ssnmaker=ssnmaker, parent=parent)

    # init

    def _buildFormLayout(self) -> Dict[str, QWidget|QLayout|None]:
        """Build the form layout for cSimpleRecordForm.

        Returns:
            FIX ME!!
            tuple: (layoutMain, layoutForm, layoutButtons) containing the main layout,
                tabbed form layout, and button layout.
        """

        rtnDict: Dict[str, QWidget|QLayout|None] = {}

        layoutMain = QVBoxLayout(self)
        layoutFormHdr = QHBoxLayout()
        layoutForm = cGridWidget(scrollable=True)
        layoutFormFixedTop = QGridLayout()
        layoutFormPages = cstdTabWidget()
        layoutFormFixedBottom = QGridLayout()
        layoutButtons = QHBoxLayout()  # may get redefined in _addActionButtons
        statusBar = QStatusBar(self)

        rtnDict['layoutMain'] = layoutMain
        rtnDict['layoutFormHdr'] = layoutFormHdr
        rtnDict['layoutForm'] = layoutForm
        rtnDict['layoutFormFixedTop'] = layoutFormFixedTop
        rtnDict['layoutFormPages'] = layoutFormPages
        rtnDict['layoutFormFixedBottom'] = layoutFormFixedBottom
        rtnDict['layoutButtons'] = layoutButtons
        rtnDict['statusBar'] = statusBar

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
        # self.showNewRecordFlag() # done when record displayed

        rtnDict['lblFormName'] = lblFormName
        rtnDict['newrecFlag'] = newrecFlag

        self.setWindowTitle(self.tr(self._formname))

        return rtnDict
    # _buildFormLayout

    import qtawesome
    def _addActionButtons(self,
            layoutButtons:QBoxLayout|None = None,
            layoutHorizontal: bool = True,
            NavActions: list[tuple[str, QIcon]]|None = None,
            CRUDActions: list[tuple[str, QIcon]]|None = None,
            ) -> None:
        """Add action buttons to the form.
        """

        _iconlib = qtawesome.icon
        dfltNavActions = [
                ("First", _iconlib("mdi.page-first")),
                ("Previous", _iconlib("mdi.arrow-left-bold")),
                ("Next", _iconlib("mdi.arrow-right-bold")),
                ("Last", _iconlib("mdi.page-last")),
        ]
        dfltCRUDActionsMain = [
                ("Add", _iconlib("mdi.plus")),
                ("Save", _iconlib("mdi.content-save")),
                ("Delete", _iconlib("mdi.delete")),
                ("Cancel", _iconlib("mdi.cancel")),
        ]
        dfltCRUDActionsSub = [
                ("Add", _iconlib("mdi.plus")),
                ("Save", _iconlib("mdi.content-save")),
                ("Delete", _iconlib("mdi.delete")),
        ]

        NavActns = NavActions if NavActions is not None else dfltNavActions
        CRUDActns = CRUDActions if CRUDActions is not None else dfltCRUDActionsMain

        if layoutHorizontal:
            self.layoutButtons = QHBoxLayout()
        else:
            self.layoutButtons = QVBoxLayout()

        # Navigation
        innerNavLayout = QHBoxLayout()
        for label, icon in NavActns:
            btn = QPushButton(label, self)
            btn.setIcon(icon)
            btn.clicked.connect(lambda _, l=label: self._handleActionButton(l))
            innerNavLayout.addWidget(btn)

            if label == "Save":
                self.btnCommit = btn
        # CRUD
        innerCRUDLayout = QHBoxLayout()
        for label, icon in CRUDActns:
            btn = QPushButton(label, self)
            btn.setIcon(icon)
            btn.clicked.connect(lambda _, l=label: self._handleActionButton(l))
            innerCRUDLayout.addWidget(btn)

            if label == "Save":
                self.btnCommit = btn

        self.layoutButtons.addLayout(innerNavLayout)
        if layoutHorizontal:
            self.layoutButtons.addSpacing(20)
        self.layoutButtons.addLayout(innerCRUDLayout)
    # _addNavButtons

    # TODO: do structure similar to _addActionButtons to allow custom button sets and define Action handlers
    #   like - duh - a dictionary
    def _handleActionButton(self, action: str) -> None:
        """Dispatch action button clicks to appropriate handler methods.

        Args:
            action (str): Action name (case-insensitive), e.g., 'first', 'save', 'delete'.
        """
        # Generic action dispatch — override if needed
        action_dict = {     # keys should be lowercase for consistency!!
            "first": self.on_loadfirst_clicked,
            "previous": self.on_loadprev_clicked,
            "next": self.on_loadnext_clicked,
            "last": self.on_loadlast_clicked,
            "add": self.on_add_clicked,
            "save": self.on_save_clicked,
            "delete": self.on_delete_clicked,
            "cancel": self.on_cancel_clicked,
        }
        action = action.lower()
        if action in action_dict:
            action_dict[action]()
        else:
            print(f"Unknown action: {action}")
            self.showError(f"Unknown action: {action}")
        #endif action
    # _handleAction

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
        for lkupwdgt in self._lookupFrmElements.values():
            lkupwdgt.refreshChoices()   # type: ignore
    # isDirty
# cSimpleRecordForm

