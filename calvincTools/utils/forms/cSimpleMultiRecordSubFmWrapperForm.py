########################
########################
# cSimpleMultiRecordForm
########################
########################

# TODO: Handle fields that need special massaging   - let the children do the heavy lifting ??
# TODO: pretty up NEW RECORD FLAG
from calvincTools.utils.cQWidgets import cGridWidget, cstdTabWidget
from calvincTools.utils.forms.cQFormWidgets import cQFmConstants, cQFmNameLabel
from calvincTools.utils.forms.cQdbFormWidgets import cQFmFldWidg, cQFmLookupWidg, cSimpRecFmElement_Base


import qtawesome
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QBoxLayout, QGridLayout, QHBoxLayout, QLabel, QLayout, QLineEdit, QMessageBox, QPushButton, QStatusBar, QTabWidget, QVBoxLayout, QWidget


from typing import Any, Dict, List


class cSimpleMultiRecordSubFmWrapperForm(QWidget):
    """
    This class serves as a container for a multi-record editing widget, providing a consistent interface and layout 
    for forms that need to display and edit multiple records at once.
    This class provides a non-ORM-tied wrapper intended to have a multi-record Widget embedded 
    (see cSimpleRecordSubForm1 and cSimpleRecordSubForm2)
    for displaying and editing multiple records in a tabular format. It is not directly tied to an ORM model, 
    but is designed to be used as a wrapper around a multi-record widget that is.

    This code borrows heavily from cSimpleRecordForm, but doesn't with ORM models, primary keys, record navigation, etc.

    Attributes:
        pages (List): List of page/tab names for multi-page forms.
        fieldDefs (Dict[str, Dict[str, Any]]): Field definitions for the form.
        others TBA

    Properties and Methods:
        _buildForm(self) -> None: where the subclass lays out its widgets.
        changeField(self, fld: cQFmFldWidg) -> None: what to do when a widget changes.
        bindField(self, fld: cQFmFldWidg, get_value: Callable[[], Any], set_value: Callable[[Any], None]) -> None: bind a field to a record attribute.
        loadRecord(self) -> None: load the current record into the form fields.
        saveRecord(self) -> None: save the form field values back to the current record.

    Properties:
        formFields (dict[str, cQFmFldWidg]): The form fields in the record. (should all be independent fields, except for the multi-record widget which will handle its own internal field-to-record mapping)

    Methods:
        getValue(self, fld: cQFmFldWidg) -> Any: Get the value of a form field.
        setValue(self, fld: cQFmFldWidg, value: Any) -> None: Set the value of a form field.

    Returns:
        _type_: _description_
    """
    # TODO: be more careful with class attributes vs instance attributes

    pages: List = []
    _tabindexTOtabname: dict[int, str] = {}
    _tabnameTOtabindex: dict[str, int] = {}
    fieldDefs: Dict[str, Dict[str, Any]] = {}

    def __init__(self,
        formname: str|None = None,
        parent: QWidget | None = None
        ):
        """
        Initialize the form with a record and optional name.

        Args:
            model (Type[Any] | None, optional): ORM model class. Defaults to None.
            formname (str | None, optional): The name of the form. Defaults to None.
            parent (QWidget | None, optional): Parent widget. Defaults to None.

        Raises:


        Args:
            rec (SQLAlchemy Model Class Instance): The record to edit.
            parent (QWidget | None, optional): The parent widget. Defaults to None.
        """

        self._formname = getattr(self, '_formname', None)
        if not self._formname:
            self._formname = formname if formname else 'Form'

        super().__init__(parent=parent)

        self._formWidgets: Dict[str, QWidget] = {}
        self._lookupFrmElements: Dict[str, QWidget] = {}    # not needed?

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

    ######################################################
    ########    Layout and field and Widget placement

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

    def _placeFields(self, layoutFormPages:QTabWidget, layoutFormFixedTop: QGridLayout|None, layoutFormFixedBottom: QGridLayout|None, lookupsAllowed: bool = False) -> None:
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
                widget = SubFormCls(parent=self)
                if not isinstance(widget, cSimpRecFmElement_Base):
                    raise TypeError(f'class {SubFormCls.__name__} must inherit from cSimpRecFmElement_Base')
                if hasattr(widget, "loadRecords") and callable(widget.loadRecords): #type: ignore
                    widget.loadRecords()    #type: ignore
            # --- Scalar case ---
            elif isLookup:
                if lookupsAllowed:
                    # but they aren't. We even threw away the sessionmaker and model info that the lookup widget would need to function, 
                    # so we can't even make the lookup widget work if we wanted to. 
                    pass
                    # if widgType not in (cDataList, cComboBoxFromDict):
                    #     widgType = cDataList  # force it to be a cDataList
                    # widget = cQFmLookupWidg(
                    #     # session_factory=ssnmkr,
                    #     # model=mdl,
                    #     lookup_field=modlFld,
                    #     lblText=lblText,
                    #     alignlblText=alignlblText,
                    #     lookupWidgType=widgType,
                    #     choices=choices,
                    #     parent=self
                    # )
                    # if lookupHandler:
                    #     if isinstance(lookupHandler, str):
                    #         if not hasattr(self, lookupHandler):
                    #             raise AttributeError(f"lookupHandler method '{lookupHandler}' not found in {self.__class__.__name__}")
                    #         lookupHandler = getattr(self, lookupHandler)
                    #     if not callable(lookupHandler):
                    #         raise TypeError("lookupHandler must be a callable function or a string name of a method")
                    #     widget.signalLookupSelected.connect(lookupHandler)
                    # self._lookupFrmElements[fldNameKey] = widget
                    # # endif lookupHandler
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
        # what database? 
        # No database, no records, just the form and its widgets. So just display the form.
        # self.initializeRec()
        # self.on_loadfirst_clicked()
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
        # no database record!!
        return
        # for widg in self._formWidgets.values():
        #     if isinstance(widg, cSimpRecFmElement_Base):
        #         widg.loadFromRecord(self.currRec())

        # self.showNewRecordFlag()
        # self.showCommitButton()
        # self.setDirty(False) - nope, don't need to set form dirty state here - isDirty checks individual fields
    # fillFormFromRec

    # TODO: wrap with fillFormFromcurrRec
    # TODO: play with positioning of new record flag
    def showNewRecordFlag(self) -> None:
        """Show or hide the 'New Record' flag based on current record state."""
        # no database record!!
        return
        # nrf = getattr(self, '_newrecFlag', None)
        # if not isinstance(nrf, QWidget):
        #     return
        # nrf.setVisible(self.isNewRecord())
    # showNewRecordFlag

    def showCommitButton(self) -> None:
        """Show the commit button if the record is dirty."""
        # no database record!!
        return
        # btnCommit = getattr(self, 'btnCommit', None)
        # if not isinstance(btnCommit, QWidget):
        #     return
        # btnCommit.setEnabled(self.isDirty())
    # showCommitButton

    ##########################################
    ########    Update

    # even though this isn't a db-based form, internal vars can get changed and need to be handled, so changeField is still relevant
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

        self.showCommitButton() #??????
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

    def _addActionButtons(self,
            layoutButtons:QBoxLayout|None = None,
            layoutHorizontal: bool = True,
            NavActions: list[tuple[str, QIcon]]|None = None,
            CRUDActions: list[tuple[str, QIcon]]|None = None,
            ) -> None:
        """Add action buttons to the form.
        """

        _iconlib = qtawesome.icon
        dfltNavActions = []
        # dfltNavActions = [
        #         ("First", _iconlib("mdi.page-first")),
        #         ("Previous", _iconlib("mdi.arrow-left-bold")),
        #         ("Next", _iconlib("mdi.arrow-right-bold")),
        #         ("Last", _iconlib("mdi.page-last")),
        # ]
        dfltCRUDActionsMain = []
        # dfltCRUDActionsMain = [
        #         ("Add", _iconlib("mdi.plus")),
        #         ("Save", _iconlib("mdi.content-save")),
        #         ("Delete", _iconlib("mdi.delete")),
        #         ("Cancel", _iconlib("mdi.cancel")),
        # ]
        dfltCRUDActionsSub = []
        # dfltCRUDActionsSub = [
        #         ("Add", _iconlib("mdi.plus")),
        #         ("Save", _iconlib("mdi.content-save")),
        #         ("Delete", _iconlib("mdi.delete")),
        # ]

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
            # "first": self.on_loadfirst_clicked,
            # "previous": self.on_loadprev_clicked,
            # "next": self.on_loadnext_clicked,
            # "last": self.on_loadlast_clicked,
            # "add": self.on_add_clicked,
            # "save": self.on_save_clicked,
            # "delete": self.on_delete_clicked,
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
    # repopLookups
# cSimpleMultiRecordSubFmWrapperForm

