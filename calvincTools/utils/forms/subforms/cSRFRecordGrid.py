from typing import Any, Type, List

from PySide6.QtCore import (
    QTimer,
 )
from PySide6.QtWidgets import (
    QAbstractItemView,
    QWidget, QPushButton,
    QTableView, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QStatusBar, 
    )

from sqlalchemy import literal, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql.elements import ColumnElement

import qtawesome

from calvincTools.utils.forms import (
    cQFmConstants,
    cSRF_Formdb_Base, cSimpRecFmElement_Base,
    cQFormLayout, cQFormBtnDef,
    )
from calvincTools.utils.cQWidgets import (
    cGridWidget, cstdTabWidget,
    )
from calvincTools.utils.SQLAlcTools import get_primary_key_column
from calvincTools.utils.cQModels import SQLAlchemyTableModel
from calvincTools.utils.strings import str2
from calvincTools.utils import pleaseWriteMe


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
        columns: List[str]|None = None,
        whereclause: Any = None,
        orderby: Any = None,
        linkFld: Any = None,
        parent_linkFld: Any = None,
        session_factory: sessionmaker[Session] | None = None,
        viewClass: Type[QTableView] = QTableView,
        viewSelectionBehavior: QAbstractItemView.SelectionBehavior = QAbstractItemView.SelectionBehavior.SelectRows,
        viewSelectionMode: QAbstractItemView.SelectionMode = QAbstractItemView.SelectionMode.ExtendedSelection,
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

        if getattr(self, '_columns', None) is None:
            self._columns = columns
        
        if getattr(self, '_whereclause', None) is None:
            self._whereclause = whereclause
        
        if getattr(self, '_orderby', None) is None:
            self._orderby = orderby
        
        self._linkFld =  getattr(self, '_linkFld', None)
        if self._linkFld is not None:
            # nothing to do - already set as class attribute
            pass
        else:
            if linkFld is not None:
                self._linkFld = getattr(self._ORMmodel, linkFld) if isinstance(linkFld, str) else linkFld # type: ignore
            # else:                
            #     raise ValueError("A linkFld must be provided either in the constructor or as a class attribute")
            # endif linkFld is not None
        # endif self._linkFld is not None

        self._parent_linkFld = getattr(self, '_parent_linkFld', None)
        if getattr(self, '_parent_linkFld', None) is not None:
            # nothing to do - already set as class attribute
            pass
        else:
            self._parent_linkFld = parent_linkFld
        # endif self._parent_linkFld is not None
        self.setParentLinkFromIncoming = self._parent_linkFld is None      # if True, when loading from parent record, set parent link field to parent's PK

        self._parentRec = None      # set in loadFromRecord
        self._recordList:list = []
        self._deleted_recordList:list = []

        # build form layout
        self._layouts: cQFormLayout= self._buildFormLayout()

        self.pages = []    # not used in this class, but needed for the layout - the subform will just use the main page and ignore the tabs
        self._page_spacing = 2
        self._buildPages()  # needed to initialize the page map for the layout, even though we won't be using multiple pages in this subform
        
        self.layoutMain = self._layouts.main
        self.table = viewClass(parent=self)
        self.table.setSelectionBehavior(viewSelectionBehavior)
        self.table.setSelectionMode(viewSelectionMode)
        if ORMmdl is None:
            raise ValueError("ORMmodel must be provided")
        if ssnmkr is None:
            raise ValueError("session_factory must be provided")
        self.Tblmodel = SQLAlchemyTableModel(
            model_class=ORMmdl, 
            session_factory=ssnmkr, 
            columns=self._columns,
            filter=literal(False), 
            orderby=self._orderby,
            parent=self
            )
        self.table.setModel(self.Tblmodel)
        self.FormPage(0).addWidget(self.table)       # type: ignore

        # Add buttons
        self._addActionButtons()

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
        parentRecordLinkField = self._parent_linkFld
        if pRec:
            retval = getattr(pRec.__class__, parentRecordLinkField) if isinstance(parentRecordLinkField, str) else parentRecordLinkField
        else:
            retval = parentRecordLinkField
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

    # -- view settings --
    def setViewSelectionBehavior(self, behavior: QAbstractItemView.SelectionBehavior):
        """Set the selection behavior of the table view.

        Args:
            behavior: QAbstractItemView.SelectionBehavior value.
        """
        self.table.setSelectionBehavior(behavior)
    def setViewSelectionMode(self, mode: QAbstractItemView.SelectionMode):
        """Set the selection mode of the table view.

        Args:
            mode: QAbstractItemView.SelectionMode value.
        """
        self.table.setSelectionMode(mode)
    # end of view settings
    
    # end of property and key widget getters/setters
    ######################################################

    ######################################################
    ########    UI  (ripped off directly from cSRF_FormUI_Base, but without the form fields and with a table instead, and with some adjustments to work as a subform within cSRFMultiRecordWrapper)

    def _buildFormLayout(self) -> cQFormLayout:
        """
        Build the form layout for this class.

        Returns:
            QFormLayout instance
        """

        layoutMain = QVBoxLayout(self)
        layoutFormHdr = QHBoxLayout()                   # not used here
        layoutForm = cGridWidget(scrollable=False)
        layoutFormFixedTop = QGridLayout()              # not used here 
        layoutFormPages = cstdTabWidget()               # the main page will be used for the table, and the tabs will just be ignored in this subform, but we need to include the tab widget in the layout to match the expected structure of cSRFMultiRecordWrapper  
        layoutFormFixedBottom = QGridLayout()           # not used here
        layoutButtons = QVBoxLayout()  
        statusBar = QStatusBar(self)

        # should this be in _finalizeMainLayout instead?
        # layoutForm.addLayout(layoutFormFixedTop, 0, 0)
        layoutForm.addWidget(layoutFormPages, 1, 0)
        # layoutForm.addLayout(layoutFormFixedBottom, 2, 0)

        # put it together
        # layoutMain.addLayout(layoutFormHdr)
        layoutMain.addWidget(layoutForm)
        layoutMain.addLayout(layoutButtons)
        # layoutMain.addWidget(statusBar)

        rtnval = cQFormLayout(
            main=layoutMain,
            header=layoutFormHdr,
            form=layoutForm,
            fixed_top=layoutFormFixedTop,
            pages=layoutFormPages,
            fixed_bottom=layoutFormFixedBottom,
            buttons=layoutButtons,
            status_bar=statusBar,

            lblFormName = None, # lblFormName, not used in this form as the subform will use the main form's name label - the subform will just display the main form's name and ignore itss own name, but we need to include it in the layout to match the expected structure of cSRFMultiRecordWrapper
            newrecFlag = None, # newrecFlag, not used in this form as there are no new records in the wrapper form - the subforms will handle their own new record status and display as needed
            )

        return rtnval
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
    def FormPage(self, idx: int | str | cQFmConstants) -> QGridLayout | None:
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

    def defineActionButtons(self):
        _iconlib = qtawesome.icon
        r = [
            # cQFormBtnDef(text="First", icon=_iconlib("mdi.page-first"), action=self.on_loadfirst_clicked),
            # cQFormBtnDef(text="Previous", icon= _iconlib("mdi.arrow-left-bold"), action=self.on_loadprev_clicked),
            # cQFormBtnDef(text="Next", icon=_iconlib("mdi.arrow-right-bold"), action=self.on_loadnext_clicked),
            # cQFormBtnDef(text="Last", icon=_iconlib("mdi.page-last"), action=self.on_loadlast_clicked),
            # cQFormBtnDef(type=cQFormBtnDef.ButtonType.NEW_HSECTION),
            cQFormBtnDef(text="Add", icon=_iconlib("mdi.plus"), action=self.add_row),
            cQFormBtnDef(text="Save", icon=_iconlib("mdi.content-save"), commitBtn=True, action=self.saveRecords),
            cQFormBtnDef(text="Delete", icon=_iconlib("mdi.delete"), action=self.del_row),
            cQFormBtnDef(text="Undo All", icon=_iconlib("mdi.undo"), action=self.on_cancel_clicked),
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
    ########    db interaction

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
        if PLFkey and self.linkFld() and rec is not None:
            conditions.append(self.linkFld() == getattr(rec, PLFkey))

        self._whereclause = conditions
        
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

            self.Tblmodel.refresh(columns=self._columns, filter=self._whereclause, orderby=self._orderby)
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

            # NOT NEEDED!! - the delete is handled by del_row, which removes from the db immediately via the session in that method. We just need to commit here.
            # delete removed
            # for rec in self._deleted_recordList:
            #     obj = session.merge(rec)
            #     session.delete(obj)

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
        rowClass = self.ORMmodel()
        if rowClass is None:
            raise ValueError("ORMmodel must be set before adding rows")
        row = rowClass()
        self._recordList.append(row)
        newpos = self.Tblmodel.rowCount()
        self.Tblmodel.insertRow(newpos)
        
        QTimer.singleShot(0, self.table.scrollToBottom)
    # add_row

    def del_row(self):
        """Delete the selected row(s) from the subform table."""
        idxs = self.table.selectionModel().selectedRows()
        for idx in sorted(idxs, key=lambda x: x.row(), reverse=True):
            rec = self.Tblmodel.record(idx.row())
            if rec in self._recordList:
                self._recordList.remove(rec)
                self._deleted_recordList.append(rec)
            self.Tblmodel.removeRow(idx.row())      # this call will also remove the record from thee db
    # del_row

    def on_cancel_clicked(self):
        """Handle cancel/undo action - discard unsaved changes and reload from database."""
        # verify this is actually what I want for the cancel button in this subform context - maybe just want to discard unsaved changes without reloading from the database, since the user can just navigate away and back to get a fresh load if they want to discard changes?
        if False:
            self.loadFromRecord(self.parentRec())
        elif False:
            # just clear the unsaved changes without reloading from the database - this will keep the current _recordList but will just refresh the view to discard unsaved changes, which should be sufficient for most use cases in this subform context, since the user can just navigate away and back to get a fresh load if they want to discard changes
            self._recordList.clear()
            self._deleted_recordList.clear()
            self.Tblmodel.refresh()   # just refresh the view to discard unsaved changes - this will not reload from the database, but will just reset the view to match the current state of the _recordList, which should have the unsaved changes removed at this point
        else:
            pleaseWriteMe("on_cancel_clicked in cSRFRecordGrid - need to decide on the desired behavior for the cancel button in this subform context - maybe just want to discard unsaved changes without reloading from the database, since the user can just navigate away and back to get a fresh load if they want to discard changes?", parent=self)
    # on_cancel_clicked
    
    ##########################################
    ########    Record Status

    # cSimpleRecordForm_Base already has this covered
# cRFRecordGrid
    def endofclass(self):
        pass