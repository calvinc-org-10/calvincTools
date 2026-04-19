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

from calvincTools.utils import get_primary_key_column
from calvincTools.database import get_cMenu_sessionmaker
from calvincTools.utils.forms.definitions.cQFormLayout import cQFormLayout

from .models import User


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
            cQFormFieldDef(name="password_hash", label=" ", widget_type=QLabel,),
            cQFormFieldDef(name="password_btn", field_type=cQFormFieldDef.cQFormFieldType.INTERNAL,
                label="Change\nPW", widget_type=QPushButton,
                on_change = self.change_password,  # type: ignore
                position=(0, 6), minimum_height=80, maximum_width=80, minimum_width=80,),
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
        # from .change_password_dialog import changePasswordDialog
        # dlg = changePasswordDialog()
        # if dlg.exec():
        #     new_pw = dlg.new_password
        #     self.set_password(new_pw)
        print ("change_password called - implement dialog to enter new password, then call set_password with new PW")
        print(f'button text is {self._formWidgets["password_btn"].widget.text()}')  # type: ignore
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
            password_hash="",  # set_password should be called to set this properly, but we'll set it to empty string for now
            active_status=True,
            is_superuser=False,
            permissions="",
            date_joined=datetime.now(),
        )
        return rec

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
        PWhint = QLabel("default PW is 'password123', but you should change it")
        layouts.fixed_top.addWidget(PWhint, 0, 0)
        
        return layouts
