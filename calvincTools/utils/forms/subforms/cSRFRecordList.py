from typing import Any, Type

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from PySide6.QtCore import Slot, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QStatusBar, QVBoxLayout, QWidget

from calvincTools.utils.forms.definitions import (
    cQFormFieldDef, 
    cQFormLayout,
    cQFormBtnDef,
    )
from calvincTools.utils.forms.widgets import cSimpRecFmElement_Base
from calvincTools.utils.forms.forms import (
    cSRF_FormUI_Base,
    cSRF_Formdb_Base,
    cSRFSingleRecordForm,
    )
from calvincTools.utils.SQLAlcTools import get_primary_key_column
from calvincTools.utils.cQWidgets import cGridWidget, cstdTabWidget


from calvincTools.utils.strings import str2


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
        layoutMain.addWidget(layoutForm)
        # layoutMain.addWidget(statusBar)

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

    def initialdisplay(self):
        return # no-op for subrecord forms since record is passed in constructor and displayed immediately
    # initialdisplay()
    
    def fillFormFromcurrRec(self):
        """Load the current record into all form fields.

        Updates all field widgets with values from the current record
        and updates the dirty and new record flags.
        """
        for Wstruc in self._formWidgets.values():
            defn = Wstruc.defn
            widg = Wstruc.widget
            if isinstance(widg, cSimpRecFmElement_Base) and defn and defn.field_type in [cQFormFieldDef.cQFormFieldType.SCALAR, cQFormFieldDef.cQFormFieldType.SUBFORM]:
                # only load from record if it's a field widget with a valid field definition - prevents trying to load from record for buttons, labels, or other non-field widgets, which would cause errors
                widg.loadFromRecord(self.currRec())

        self.showNewRecordFlag()
        self.showCommitButton()
        # self.setDirty(False) - nope, don't need to set form dirty state here - isDirty checks individual fields
    # fillFormFromRec

    # TODO: wrap with fillFormFromcurrRec
    # TODO: play with positioning of new record flag
    def showNewRecordFlag(self) -> None:
        """Show or hide the 'New Record' flag based on current record state."""
        nrf = self._layouts.newrecFlag
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
    def endofclass(self):
        pass
####################################################################
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
        recordClass: Type[cSRFRecordList_Record]|None = None,   
        parent:QWidget|None=None,
        *args, **kwargs):

        self.vwClass = viewClass
        super().__init__(model=ORMmodel, ssnmaker=session_factory, parent=parent)

        if getattr(self, '_ORMmodel', None) is None:
            self.setORMmodel(ORMmodel)
        if self._ORMmodel is not None:
            self._primary_key = get_primary_key_column(self._ORMmodel)

        if getattr(self, '_recordClass', None) is None:
            self._recordClass = recordClass
        if self._recordClass is None:
            self._recordClass = cSRFRecordList_Record   # default record class for list-based subforms - can be overridden by passing in constructor or setting as class attribute


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
            self._parent_linkFld = parent_linkFld # type: ignore
        # endif self._parent_linkFld is not None
        # if setParentLinkFromIncoming, when loading from parent record, set parent link field to parent's PK
        self.setParentLinkFromIncoming = self._parent_linkFld is None   # if parent_linkFld provided in constructor, only set from incoming if it's None

        if not getattr(self, '_ssnmaker', None):
            self._ssnmaker = getattr(parent, '_ssnmaker', None)
        if not self._ssnmaker:
            raise ValueError(f"A sessionmaker must be provided defined in the parent form {parent}")

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
        assert self._recordClass is not None, "recordClass must be set to add display rows"
        wdgt = self._recordClass(rec, parent=self)
        QLWitm = QListWidgetItem()
        QLWitm.setSizeHint(wdgt.sizeHint())
        self.dispArea.addItem(QLWitm)
        self.dispArea.setItemWidget(QLWitm, wdgt)

        QTimer.singleShot(0, self.dispArea.scrollToBottom)
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

    def loadFromRecord(self, rec=None, *caller_conditions):
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
            # end for
        # del_row
# cSRFRecordList_Record
    def endofclass(self):
        pass