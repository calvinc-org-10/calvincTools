from typing import Any, Type

from PySide6.QtWidgets import (
    QAbstractItemView,
    QTableView, QVBoxLayout,
    )

from sqlalchemy import literal, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql.elements import ColumnElement

from calvincTools.utils.forms.forms.cSRF_Formdb_Base import cSRF_Formdb_Base
from calvincTools.utils.forms.widgets.cSimpRecFmElement_Base import cSimpRecFmElement_Base
from calvincTools.utils.SQLAlcTools import get_primary_key_column
from calvincTools.utils.cQModels import SQLAlchemyTableModel
from calvincTools.utils.strings import str2


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
        self.setParentLinkFromIncoming = self._parent_linkFld is None      # if True, when loading from parent record, set parent link field to parent's PK

        self._parentRec = None      # set in loadFromRecord
        self._recordList:list = []
        self._deleted_recordList:list = []

        self.layoutMain = QVBoxLayout(self)
        self.table = viewClass(parent=self)
        self.table.setSelectionBehavior(viewSelectionBehavior)
        self.table.setSelectionMode(viewSelectionMode)
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
        if PLFkey and self.linkFld() and rec is not None:
            conditions.append(self.linkFld() == getattr(rec, PLFkey))

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

    ##########################################
    ########    Record Status

    # cSimpleRecordForm_Base already has this covered
# cRFRecordGrid
    def endofclass(self):
        pass