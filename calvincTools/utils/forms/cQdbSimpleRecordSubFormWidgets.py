from PySide6.QtGui import QFont

from calvincTools.utils.SQLAlcTools import get_primary_key_column
from calvincTools.utils.cQModels import SQLAlchemyTableModel
from calvincTools.utils.cQWidgets import cGridWidget, cstdTabWidget
from calvincTools.utils.forms.cQdbFormWidgets import cSimpRecFmElement_Base
from calvincTools.utils.forms.cQdbSimpleRecordFormWidgets import cSimpleRecordForm_Base
from calvincTools.utils.strings import str2


from PySide6.QtWidgets import QBoxLayout, QGridLayout, QHBoxLayout, QLabel, QLayout, QListWidget, QListWidgetItem, QPushButton, QStatusBar, QTabWidget, QTableView, QVBoxLayout, QWidget
from sqlalchemy import literal, select
from sqlalchemy.orm import Session, sessionmaker


from typing import Any, Dict, Type


class cSimpleRecordSubForm1(cSimpRecFmElement_Base):
    # does not need to inherit from cSimpleRecordForm_Base
    # since this is mainly wrapping a table with multiple records
    """
    Generic subform widget to handle a one-to-many relationship using a table view.

    This widget displays related records in a table format with add/delete functionality.
    It manages the relationship between a parent record and multiple child records.
    Ex: parts_needed for a WorkOrder.

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
        parent=None
        ):
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
        super().__init__(parent)

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

        self.setParentLinkFromIncoming = False      # if True, when loading from parent record, set parent link field to parent's PK
        if getattr(self, '_parent_linkFld', None) is not None:
            # nothing to do - already set as class attribute
            pass
        else:
            self._parent_linkFld = parent_linkFld
            self.setParentLinkFromIncoming = True
        # endif self._parent_linkFld is not None

        if not self._ssnmaker:
            if not session_factory:
                raise ValueError("A sessionmaker must be provided either in the constructor or as a class attribute")
            self._ssnmaker = session_factory

        self._parentRec = None  # set by parent form when loading
        self._childRecs:list = []
        self._deleted_childRecs:list = []

        self.layoutMain = QVBoxLayout(self)
        self.table = viewClass(parent=self)
        self.Tblmodel = SQLAlchemyTableModel(self._ORMmodel, self._ssnmaker, literal(False), parent=self)
        self.table.setModel(self.Tblmodel)
        self.layoutMain.addWidget(self.table)

        # not now... mebbe later ...
        # # action buttons for add/remove
        # btnLayout = QHBoxLayout()
        # self.btnAdd = QPushButton("Add")
        # self.btnDel = QPushButton("Delete")
        # btnLayout.addWidget(self.btnAdd)
        # btnLayout.addWidget(self.btnDel)
        # self.layoutMain.addLayout(btnLayout)

        # self.btnAdd.clicked.connect(self.add_row)
        # self.btnDel.clicked.connect(self.del_row)
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
    def loadFromRecord(self, rec, *caller_conditions):
        """Load subrecords for the given parent record."""
        self.setparentRec(rec)
        self._childRecs.clear()
        self._deleted_childRecs.clear()

        PLFkey = self.parent_linkFld_keystr(rec)

        # implement later - verify that caller_conditions are valid SQLAlchemy expressions
        # from sqlalchemy.sql.elements import ColumnElement

        # for c in caller_conditions:
        #     if not isinstance(c, ColumnElement):
        #         raise TypeError(f"Invalid condition: {c!r}")
        conditions = list(caller_conditions)
        if rec is not None:
            conditions.append(self._linkFld == getattr(rec, PLFkey))

        with self._ssnmaker() as session:
            stmt = select(self._ORMmodel).where(*conditions)
            rows = session.scalars(stmt).all()
            for r in rows:
                session.expunge(r)
            self._childRecs.extend(rows)

            self.Tblmodel.refresh(filter=*conditions) # type: ignore
        #endwith
    def loadRecords(self, *caller_conditions):
        """Load records - assumes no parent record """
        return self.loadFromRecord(None, caller_conditions)
    # loadFromRecord

    def saveToRecord(self, rec):
        """Save subrecords back to database."""
        parntRec = self.parentRec()
        if parntRec != rec:
            raise ValueError("Parent record mismatch on saveToRecord")

        PLFkey = self.parent_linkFld_keystr(rec)

        with self._ssnmaker() as session:
            # reattach new/edited
            for rec in self._childRecs:
                if parntRec is not None:
                    setattr(rec, self._linkFld.key, getattr(parntRec, PLFkey)) # type: ignore
                session.merge(rec)

            # delete removed
            for rec in self._deleted_childRecs:
                if getattr(rec, PLFkey, None) is not None or parntRec is None: # type: ignore
                    obj = session.merge(rec)
                    session.delete(obj)

            session.commit()
        # endwith

        self._deleted_childRecs.clear()
    # saveForParent

    # --- Internal helpers ---

    def add_row(self):
        """Add a new empty row to the subform table."""
        row = self.ORMmodel()
        if self.parentRec() is not None:
            setattr(row, self.linkFld().key, getattr(self.parentRec(), self.parent_linkFld_keystr(), None)) # type: ignore
        self.Tblmodel.insertRow(row)
    # add_row

    def del_row(self):
        """Delete the selected row(s) from the subform table."""
        idxs = self.table.selectionModel().selectedRows()
        for idx in sorted(idxs, key=lambda x: x.row(), reverse=True):
            rec = self.Tblmodel.record(idx.row())
            if rec in self._childRecs:
                self._childRecs.remove(rec)
                self._deleted_childRecs.append(rec)
            self.Tblmodel.removeRow(idx.row())
        # end for
    # del_row
# cSimpleRecordSubForm1

class cSimpRecSbFmRecord(cSimpRecFmElement_Base, cSimpleRecordForm_Base):
    """A form element representing a single subrecord.

    This class wraps a single child record in a form-like interface for use
    within a parent form's subform list. It does not have navigation buttons.
    """
# class cSimpRecSbFmRecord(cSimpRecFmElement_Base, cSimpleRecordForm):
# nope, don't inherit from cSimpleRecordForm - that double-defines layouts, buttons, etc. Copy what we need from it instead.

    # def __init__(self, rec: Any, parent:"cSimpleRecordSubForm2|None"=None):
    def __init__(self, rec: Any, parent:QWidget|None=None):
        """Initialize a subrecord form element.

        Args:
            rec (Any): ORM record to display.
            parent (QWidget | None, optional): Parent widget. Defaults to None.

        Raises:
            ValueError: If rec doesn't have an ORM class or parent doesn't have sessionmaker.
        """
        self._ORMmodel = rec.__class__  # cannot use setORMmodel here because super not yet initialized
        if not self._ORMmodel:
            raise ValueError(f"{rec} should be a record with an ORM class")
        # self._primary_key = get_primary_key_column(self._ORMmodel)

        self._ssnmaker = getattr(parent, '_ssnmaker', None)
        if not self._ssnmaker:
            raise ValueError(f"A sessionmaker must be provided defined in the parent form {parent}")

        self.fieldDefs = getattr(parent, 'fieldDefs', {})

        super().__init__(parent=parent)

        # initialdisplay(self):
        self.setcurrRec(rec)
        self.loadFromRecord(rec)
        # self.showNewRecordFlag(self.isNewRecord())
    # __init__

    def _buildFormLayout(self) -> Dict[str, QWidget|QLayout|None]:
        """Build the layout for a subrecord form element.

        Returns:
            tuple: (layoutMain, layoutForm, layoutButtons) where layoutButtons is None.
        """

        rtnDict: Dict[str, QWidget|QLayout|None] = {}

        layoutMain = QVBoxLayout(self)
        layoutForm = cGridWidget(scrollable=True)
        layoutFormFixedTop = QGridLayout()
        layoutFormPages = cstdTabWidget()
        layoutFormFixedBottom = QGridLayout()
        self._statusBar = QStatusBar(self)

        # should this be in _finalizeMainLayout instead?
        layoutForm.addLayout(layoutFormFixedTop, 0, 0)
        layoutForm.addWidget(layoutFormPages, 1, 0)
        layoutForm.addLayout(layoutFormFixedBottom, 2, 0)

        rtnDict['layoutMain'] = layoutMain
        rtnDict['layoutForm'] = layoutForm
        rtnDict['layoutFormFixedTop'] = layoutFormFixedTop
        rtnDict['layoutFormPages'] = layoutFormPages
        rtnDict['layoutFormFixedBottom'] = layoutFormFixedBottom
        rtnDict['statusBar'] = self._statusBar
        # this is only being returned becxause parent class expects it
        # but subrecord forms don't have action buttons
        rtnDict['layoutButtons'] = QHBoxLayout()  # dummy

        self._newrecFlag = QLabel("New Rec", self)
        fontNewRec = QFont()
        fontNewRec.setBold(True)
        fontNewRec.setPointSize(10)
        fontNewRec.setItalic(True)
        self._newrecFlag.setFont(fontNewRec)
        self._newrecFlag.setStyleSheet("color: red;")
        layoutMain.addWidget(self._newrecFlag) # at top for visibility - different from main form

        rtnDict['newrecFlag'] = self._newrecFlag

        return rtnDict
    # _buildFormLayout

    def initialdisplay(self):
        """Initialize display (no-op for subrecord forms since record is passed in constructor)."""
        # this is a noop here since record is passed in constructor
        return
    # initialdisplay()

    #############################################################
    ########    overrides of cSimpleRecordForm_Base methods
    #############################################################

    # def _placeFields(self, lookupsAllowed: bool = False) -> None:
    def _placeFields(self, layoutFormPages:QTabWidget, layoutFormFixedTop: QGridLayout|None, layoutFormFixedBottom: QGridLayout|None, lookupsAllowed: bool = True) -> None:
        """Place fields with lookups disabled."""
        return super()._placeFields(layoutFormPages, layoutFormFixedTop, layoutFormFixedBottom, lookupsAllowed = False)
    # _placeFields

    def _addActionButtons(self, layoutButtons:QBoxLayout|None) -> None:
        """Add action buttons (none for subrecords)."""
        # no navigation buttons for subrecords
        return
    # _addActionButtons
    def _handleActionButton(self, action: str) -> None:
        """Handle action button clicks.

        Args:
            action (str): Action name.

        Note:
            No action buttons for subrecords.
        """
        # no action buttons for subrecords
        return
    # _handleAction


    def loadFromRecord(self, rec: object) -> None:
        """Fill widget from ORM record."""
        currRec = self.currRec()
        if currRec != rec:
            self.setcurrRec(rec)
        self.fillFormFromcurrRec()
    # loadFromRecord

    def saveToRecord(self, rec: object) -> None:
        """Push widget state into ORM record."""
        self.on_save_clicked()
    # saveToRecord

    # def isDirty(self) -> bool:
    #     """Return True if the widget's value differs from what was loaded."""
    #     return False
    # # isDirty


    def setDirty(self, dirty: bool = True, sendSignal:bool = True) -> None:
        """Mark the subform as dirty.

        Args:
            dirty (bool, optional): Whether to mark as dirty. Defaults to True.
            sendSignal (bool, optional): Whether to emit signal. Defaults to True.

        Note:
            Subforms don't track their own dirty state; they poll children instead.
        """
        """Mark the field/subform as dirty."""
        return
    # setDirty
# cSimpRecSbFmRecord
class cSimpleRecordSubForm2(cSimpRecFmElement_Base, cSimpleRecordForm_Base):
    """Generic subform widget to handle a one-to-many relationship using individual record forms.

    Unlike cSimpleRecordSubForm1 which uses a table view, this class presents each
    child record in its own form widget within a list. This provides more detailed
    editing capabilities for complex child records.

    Generic subform widget to handle a one-to-many relationship.
    Ex: parts_needed for a WorkOrder.

    Presents records in cSimpRecSbFmRec's

    Attributes:
        _parentFK: Foreign key field linking to the parent record. May be none if no parent record. 
        _parentRec: Reference to the parent record. May be None if not set or if parent record is deleted.
        _parentRecPK: Primary key of the parent record. May be None if parent record is new and not yet saved or if no parent record.
        _childRecs (list): List of child records.
        _deleted_childRecs (list): List of child records pending deletion.
        dispArea: QListWidget containing the child record forms.

    Args:
        ORMmodel (Type[Any]): ORM model for the subrecords
        parentFK (InstrumentedAttribute): relationship FK field in the parent model. May be None if no parent record.
        session_factory (sessionmaker): SQLAlchemy sessionmaker
        parent (QWidget | None): parent widget
    """


    # NEXT: make viewClass QListWidget (was QTableView)
    def __init__(self,
        ORMmodel: Type[Any]|None = None,
        linkFld: Any = None,
        parent_linkFld: Any = None,
        session_factory: sessionmaker[Session] | None = None,
        viewClass: Type[QListWidget] = QListWidget,
        parent=None
        ):
        """Initialize a list-based subform for one-to-many relationships.

        Args:
            ORMmodel (Type[Any] | None, optional): ORM model for subrecords. Defaults to None.
            linkFld: Any = None,
            parent_linkFld: Any = None,
            session_factory (sessionmaker[Session] | None, optional): Database session factory. Defaults to None.
            viewClass (Type[QListWidget], optional): List view class. Defaults to QListWidget.
            parent (optional): Parent widget. Defaults to None.

        Raises:
            ValueError: If required parameters not provided.
        """

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

        self.setParentLinkFromIncoming = False      # if True, when loading from parent record, set parent link field to parent's PK
        if getattr(self, '_parent_linkFld', None) is not None:
            # nothing to do - already set as class attribute
            pass
        else:
            self._parent_linkFld = parent_linkFld # type: ignore
            self.setParentLinkFromIncoming = True
        # endif self._parent_linkFld is not None

        if not self._ssnmaker:
            if not session_factory:
                raise ValueError("A sessionmaker must be provided either in the constructor or as a class attribute")
            self._ssnmaker = session_factory

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
    ########    Layout and field and Widget placement

    def _buildFormLayout(self) -> Dict[str, QWidget|QLayout|None]:
        """Build the form layout for list-based subform.

        Returns:
            tuple: (layoutMain, layoutForm, layoutButtons) containing layouts.
        """

        rtnDict: Dict[str, QWidget|QLayout|None] = {}

        layoutMain = QVBoxLayout(self)
        layoutForm = cGridWidget(scrollable=True)
        layoutFormFixedTop = QGridLayout()
        layoutFormPages = cstdTabWidget()
        layoutFormFixedBottom = QGridLayout()
        layoutButtons = QHBoxLayout()  # may get redefined in _addActionButtons
        self._statusBar = QStatusBar(self)

        rtnDict['layoutMain'] = layoutMain
        rtnDict['layoutForm'] = layoutForm
        rtnDict['layoutFormFixedTop'] = layoutFormFixedTop
        rtnDict['layoutFormPages'] = layoutFormPages
        rtnDict['layoutFormFixedBottom'] = layoutFormFixedBottom
        rtnDict['layoutButtons'] = layoutButtons
        rtnDict['statusBar'] = self._statusBar

        # should this be in _finalizeMainLayout instead?
        layoutForm.addLayout(layoutFormFixedTop, 0, 0)
        layoutForm.addWidget(layoutFormPages, 1, 0)
        layoutForm.addLayout(layoutFormFixedBottom, 2, 0)

        viewClass = self.vwClass if hasattr(self, 'vwClass') else QListWidget
        self.dispArea = viewClass(parent=self)
        layoutFormPages.addTab(self.dispArea, '')
        # self.Tblmodel = SQLAlchemyTableModel(self._model, self._ssnmaker, literal(False), parent=self)
        # FIXMEFIXMEFIXME!!!
        # not needed? each record widget handles its own data
        # self.dispArea.setModel(self.Tblmodel)  # yhis shouldn't work - change to handle link table <-> Tblmodel internally - use _childRecs?
        # self.layoutMain.addWidget(self.dispArea)

        return rtnDict
    # _buildFormLayout

    def _buildPages(self, layoutFormPages: QTabWidget) -> None:
        """Build pages (not used for list-based subforms - single page only)."""
        # nope, just the one page
        return
    # _buildPages

    # def _finalizeMainLayout(self):
    #     assert isinstance(self.layoutMain, QBoxLayout), 'layoutMain must be a Box Layout'

    #     lyout = getattr(self, 'layoutFormHdr', None)
    #     if isinstance(lyout, QLayout):
    #         self.layoutMain.addLayout(lyout)
    #     lyout = getattr(self, 'layoutForm', None)
    #     if isinstance(lyout, QLayout):
    #         self.layoutMain.addLayout(lyout)
    #     lyout = getattr(self, 'layoutButtons', None)
    #     if isinstance(lyout, QLayout):
    #         self.layoutMain.addLayout(lyout)
    #     lyout = getattr(self, '_statusBar', None)
    #     if isinstance(lyout, QLayout):
    #         self.layoutMain.addLayout(lyout)            #TODO: more flexibility in where status bar is placed
    # # _finalizeMainLayout

    def _placeFields(self, layoutFormPages:QTabWidget, layoutFormFixedTop: QGridLayout|None, layoutFormFixedBottom: QGridLayout|None, lookupsAllowed: bool = True) -> None:
        """Place fields (handled by _addDisplayRow for list-based subforms)."""
        # field placement handled by _addDisplayRow, since they are placed in a list
        return
    # _placeFields

    def _addActionButtons(self, layoutButtons:QBoxLayout|None) -> None:
        """Add Add and Delete buttons to the subform."""
        # action buttons for add/remove
        # btnLayout = self.layoutButtons
        btnLayout = layoutButtons
        assert isinstance(btnLayout, QBoxLayout), "layoutButtons must be a Box Layout"
        self.btnAdd = QPushButton("Add")
        self.btnDel = QPushButton("Delete")
        btnLayout.addWidget(self.btnAdd)
        btnLayout.addWidget(self.btnDel)

        self.btnAdd.clicked.connect(self.add_row)
        self.btnDel.clicked.connect(self.del_row)
    # _addActionButtons


    ######################################################
    ########    Display 

    def initialdisplay(self):
        """Initialize display (not used - record passed in constructor)."""
        # not used here - record passed in constructor
        return
    # initialdisplay()

    def _addDisplayRow(self, rec):
        """Add a display row for the given record."""
        # does NOT add to _childRecs - that must be done separately (document why)
        wdgt = cSimpRecSbFmRecord(rec, parent=self)
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
            qry = select(modl).where(*conditions)
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
        return self.loadFromRecord(None, caller_conditions)
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
    # @Slot()
    # def setDirty(self, wdgt, dirty: bool = True):
    #     """Mark dirty state (currently a no-op as dirty tracking is delegated to child elements)."""
    #     # rethink - adapters handle their own dirty state
    #     # so all that needs to be set here is self.dirty
    #     # right?

    #     # better yet, self doesn't need to track its dirty state
    #     # since  isDirty will poll children

    #     # keep an eye on the time the polling takes
    #     # if it's excessive, find the best way to record child dirty states

    #     return
    # # setFormDirty

    # def isDirty(self, widg = None) -> bool:
    #     """Check if any child form element is dirty.
        
    #     Returns:
    #         bool: True if any child element has been modified, False otherwise.
    #     """
    #     # poll children; if one is Dirty, form is Dirty
    #     if widg is None:
    #         widg = self
            
    #     # poll children; if one is Dirty, form is Dirty
    #     for FmElement in widg.children():
    #         if not isinstance(FmElement, cSimpRecFmElement_Base):
    #             dirtyState = self.isDirty(FmElement)
    #             if dirtyState:
    #                 return True
    #             else:
    #                 continue
    #         elif FmElement.isDirty():
    #             return True
    #         else:
    #             continue
    #     #endfor FmElement in self.children():
        
    #     return False
    # # isDirty

#endclass cSubRecordForm2

