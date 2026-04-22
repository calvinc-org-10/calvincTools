from typing import List
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, 
    QLineEdit, QCheckBox, QLabel, QPushButton,
    )

from calvincTools.utils.forms import (
    cSRFMultiRecordWrapper, cSRFRecordList, cSRFRecordList_Record,
    cQFormFieldDef, cQFormLayout,
    )
from calvincTools.models import cParameters
from calvincTools.utils import get_primary_key_column
from calvincTools.database import (get_cMenu_sessionmaker, Repository, )
from calvincTools.utils.forms.definitions.cQFormLayout import cQFormLayout

from .models import User
from .pwegg import hash_password
from .chngPW_dlg import chngPW_dlg
from .decorators import (active_user_required, superuser_required, )

_parmKey = cParameters.ParmName == "DFLT-NEW-PW"
_dfltNewPW_rec = Repository(get_cMenu_sessionmaker(), cParameters).get_all(_parmKey)
_dfltNewPW_rec = _dfltNewPW_rec[0] if _dfltNewPW_rec else None
_dfltNewPW = getattr(_dfltNewPW_rec, "ParmValue", "password123")

class userEditFmRecord(cSRFRecordList_Record):
    _ORMmodel = User
    _primary_key = get_primary_key_column(User)
    _ssnmaker = get_cMenu_sessionmaker()
        
    def defineFields(self) -> List[cQFormFieldDef] | None:
        flds = [
            cQFormFieldDef(name="id", label="|", label_alignment = Qt.AlignmentFlag.AlignRight, 
                widget_type=QLabel, readonly=True,
                position=(0, 0), minimum_width=50,),
            cQFormFieldDef(name="username", label="|", label_alignment = Qt.AlignmentFlag.AlignRight, 
                widget_type=QLineEdit,
                position=(0, 1), minimum_width=150,),
            cQFormFieldDef(name="first_name", label="|", label_alignment = Qt.AlignmentFlag.AlignRight, 
                widget_type=QLineEdit,
                position=(0, 2), minimum_width=150,),
            cQFormFieldDef(name="last_name", label="|", label_alignment = Qt.AlignmentFlag.AlignRight, 
                widget_type=QLineEdit,
                position=(0, 3), minimum_width=150,),
            cQFormFieldDef(name="email", label="|", label_alignment = Qt.AlignmentFlag.AlignRight, 
                widget_type=QLineEdit,
                position=(0, 4), minimum_width=175, ),
            cQFormFieldDef(name="password_optional", label="|", widget_type=QCheckBox,
                lblChkBxYesNo={True: "PW-OPT", False: ""},
                position=(0, 5),),
            cQFormFieldDef(name="password_hash", label=" ", widget_type=QLabel, invisible=True,),  # hidden field to store PW hash, not editable
            cQFormFieldDef(name="password_btn", field_type=cQFormFieldDef.cQFormFieldType.INTERNAL,
                label="Change\nPW", widget_type=QPushButton,
                on_change = self.change_password,  # type: ignore
                position=(0, 6),),
            cQFormFieldDef(name="active_status", label="|", widget_type=QCheckBox,
                lblChkBxYesNo={True: "ACTV", False: "INACTV"},
                position=(0, 7),),
            cQFormFieldDef(name="is_superuser", label="|", widget_type=QCheckBox,
                lblChkBxYesNo={True: "SPUSR", False: ""},
                position=(0, 8),),
            cQFormFieldDef(name="permissions", label="|", label_alignment = Qt.AlignmentFlag.AlignRight, 
                widget_type=QLineEdit,
                position=(0, 9), minimum_width=200,),
            cQFormFieldDef(name="menuGroup", label="|", label_alignment = Qt.AlignmentFlag.AlignRight, 
                widget_type=QLineEdit,
                position=(0, 10), minimum_width=50,),
            cQFormFieldDef(name="date_joined", label="date joined:", widget_type=QLabel, readonly=True,
                position=(1, 0, 1, 2),),
            cQFormFieldDef(name="last_login", label="last login:", widget_type=QLabel, readonly=True,
                position=(1, 3, 1, 2),),
            ]
        return flds
    # defineFields

    def change_password(self):
        # # for security, changing PW requires entering new PW in a dialog
        dlg = chngPW_dlg()
        id = self.currRec().id  # type: ignore
        dlg.exec_chg_PW(id, require_oldPW=False)  # type: ignore
    # change_password
        
class userEditFm(cSRFRecordList):
    _ORMmodel = User
    _primary_key = get_primary_key_column(User)
    _ssnmaker = get_cMenu_sessionmaker()
    _recordClass = userEditFmRecord
    
    def defineFields(self) -> List[cQFormFieldDef] | None:
        return None # fields are defined in record class
        # ?? return []
        
    def _buildFormLayout(self) -> cQFormLayout:
        layouts = super()._buildFormLayout()
        
        def add_hdr_col(label, size, col):
            wdgt = QLabel(label)
            wdgt.setMinimumWidth(size)
            layouts.fixed_top.addWidget(wdgt, 0, col)

        # add header row
        add_hdr_col("ID", 50, 0)
        add_hdr_col("Username", 150, 1)
        add_hdr_col("First Name", 150, 2)
        add_hdr_col("Last Name", 150, 3)
        add_hdr_col("Email", 175, 4)
        add_hdr_col("Password", 30, 5)
        # add_hdr_col(" ", 10, 6)  # for change PW button
        add_hdr_col("Status", 80, 7)
        add_hdr_col("Superuser", 80, 8)
        add_hdr_col("Permissions", 60, 9)
        add_hdr_col("Menu Group", 20, 10)
        
        return layouts
    
    def new_record(self):
        # override new_record to set default values for new user records
        rec = User(
            username="newuser",
            first_name="New",
            last_name="User",
            email="",
            password_optional=False,
            password_hash='',
            active_status=True,
            is_superuser=False,
            permissions="",
            date_joined=datetime.now(),
        )
        rec.set_password(_dfltNewPW)  # set default password for new users
        return rec

@superuser_required
# mebbe later create a permission specifically for user management and require that instead of superuser status, but for now I'll just require superuser status since that's easier and will work for testing - I can always change it to a specific permission later when I have that available if I decide that's more appropriate
class editUsersForm(cSRFMultiRecordWrapper):
    _formname = "Edit Users"
    
    def defineFields(self) -> List[cQFormFieldDef] | None:
        flds = [
            cQFormFieldDef(name="userList", field_type=cQFormFieldDef.cQFormFieldType.SUBFORM,
                widget_type=userEditFm,
                position=(0, 0),),
            ]

        return flds

    def _buildFormLayout(self) -> cQFormLayout:
        layouts = super()._buildFormLayout()
        
        # set form width
        self.setMinimumWidth(1500)
        
        # add hints in header
        PWhint = QLabel(f"default PW is '{_dfltNewPW}' for new users - change after creating user")
        layouts.fixed_top.addWidget(PWhint, 0, 0)
        
        return layouts
