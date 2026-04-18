
from typing import List

from PySide6.QtWidgets import (QWidget, 
    QLineEdit, QCheckBox, QLabel,
    )

from calvincTools.utils.forms import (
    cSRFMultiRecordWrapper, cSRFRecordList, cSRFRecordList_Record,
    cQFormFieldDef,
    )

from calvincTools.utils import get_primary_key_column
from calvincTools.database import get_cMenu_sessionmaker

from .models import User


class userEditFmRecord(cSRFRecordList_Record):
    _ORMmodel = User
    _primary_key = get_primary_key_column(User)
    _ssnmmaker = get_cMenu_sessionmaker()
        
    def defineFields(self) -> List[cQFormFieldDef] | None:
        flds = [
            cQFormFieldDef(name="id", label="|", widget_type=QLineEdit, readonly=True,
                position=(0, 0),),
            cQFormFieldDef(name="username", label="|", widget_type=QLineEdit,
                position=(0, 1),),
            cQFormFieldDef(name="first_name", label="|", widget_type=QLineEdit,
                position=(0, 2),),
            cQFormFieldDef(name="last_name", label="|", widget_type=QLineEdit,
                position=(0, 3),),
            cQFormFieldDef(name="email", label="|", widget_type=QLineEdit,
                position=(0, 4),),
            cQFormFieldDef(name="password_optional", label="|", widget_type=QCheckBox,
                lblChkBxYesNo={True: "OPTIONAL", False: ""},
                position=(0, 5),),
            cQFormFieldDef(name="password_hash", label="|", widget_type=QLabel,
                position=(0, 6),),
            cQFormFieldDef(name="active_status", label="|", widget_type=QCheckBox,
                lblChkBxYesNo={True: "ACTIVE", False: "INACTIVE"},
                position=(0, 7),),
            cQFormFieldDef(name="is_superuser", label="|", widget_type=QCheckBox,
                lblChkBxYesNo={True: "SUPERUSER", False: ""},
                position=(0, 8),),
            cQFormFieldDef(name="permissions", label="|", widget_type=QLineEdit,
                position=(0, 9),),
            cQFormFieldDef(name="menuGroup", label="|", widget_type=QLineEdit,
                position=(0, 10),),
            cQFormFieldDef(name="date_joined", label="date joined", widget_type=QLineEdit,
                position=(1, 0, 1, 3),),
            cQFormFieldDef(name="last_login", label="last login", widget_type=QLineEdit,
                position=(1, 5, 1, 3),),
            ]
        return flds

class userEditFm(cSRFRecordList):
    _ORMmodel = User
    _primary_key = get_primary_key_column(User)
    _ssnmmaker = get_cMenu_sessionmaker()
    _recordClass = userEditFmRecord
    
    def defineFields(self) -> List[cQFormFieldDef] | None:
        return None # fields are defined in record class
        # ?? return []

class editUsersForm(cSRFMultiRecordWrapper):
    _formname = "Edit Users"
    
    def defineFields(self) -> List[cQFormFieldDef] | None:
        flds = [
            cQFormFieldDef(name="userList", field_type=cQFormFieldDef.cQFormFieldType.SUBFORM,
                widget_type=userEditFm,
                position=(0, 0),),
            ]
        return flds