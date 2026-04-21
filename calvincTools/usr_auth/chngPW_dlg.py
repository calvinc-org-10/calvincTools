from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QDialogButtonBox, QVBoxLayout, QMessageBox,
)

from calvincTools.database import get_cMenu_sessionmaker, Repository
from calvincTools.utils.forms import cQFmFldWidg

from .models import User
from .pwegg import change_password, verify_password


class chngPW_dlg(QDialog):

    def __init__(self, parent = None):   # parent:QWidget = None
        super().__init__(parent)

        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setWindowTitle(self.tr('Change Password'))

        self.dlgButtons = None # self.dlgButtons:QDialogButtonBoxto be defined later, but must exist now

        lblDlgTitle = QLabel(self.tr('Change Password'))

        self.pw_old = cQFmFldWidg(widgType=QLineEdit, lblText=self.tr('Old Password'), parent=self)
        self.pw_old.signalFldChanged.connect(self.enableOKButton)   # enable OK button only when all PW info is given and valid
        # self.pw_old.setEchoMode(QLineEdit.EchoMode.Password)
        self.pw_new = cQFmFldWidg(widgType=QLineEdit, lblText=self.tr('New Password'), parent=self)
        self.pw_new.signalFldChanged.connect(self.check_pwnew_confirm)   # check if new PW and confirm match whenever new PW is changed
        # self.pw_new.setEchoMode(QLineEdit.EchoMode.Password)
        self.pw_new_confirm = cQFmFldWidg(widgType=QLineEdit, lblText=self.tr('Confirm New Password'), parent=self)
        self.pw_new_confirm.signalFldChanged.connect(self.check_pwnew_confirm)   # check if new PW and confirm match whenever confirm PW is changed
        # self.pw_new_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.dlgButtons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel,
            Qt.Orientation.Horizontal,
            )
        self.dlgButtons.accepted.connect(self.accept)
        self.dlgButtons.rejected.connect(self.reject)
        self.dlgButtons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)

        layoutMine = QVBoxLayout()
        layoutMine.addWidget(lblDlgTitle)
        layoutMine.addWidget(self.pw_old)
        layoutMine.addWidget(self.pw_new)
        layoutMine.addWidget(self.pw_new_confirm)
        layoutMine.addWidget(self.dlgButtons)

        self.setLayout(layoutMine)
    # __init__
    
    ##########################################
    ########    execute this dialog

    def exec_chg_PW(self, userID:int, require_oldPW:bool = True) -> None:
        self.required_oldPW = require_oldPW
        if not require_oldPW:
            self.pw_old.setVisible(False)
        ret = super().exec()
        if ret == QDialog.DialogCode.Accepted:
            self.usrRec = Repository(get_cMenu_sessionmaker(),User).get_by_id(userID)
            assert self.usrRec, f"User with ID {userID} not found."
            
            oldPW_entrd = self.pw_old.text() if require_oldPW else None
            if require_oldPW and not self.usrRec.check_password(oldPW_entrd):
                QMessageBox.critical(self, self.tr('Error'), self.tr('Old password is required.'))
                return None

            newPW = self.pw_new.text()
            newPW_confirm = self.pw_new_confirm.text()
            if newPW != newPW_confirm:
                QMessageBox.critical(self, self.tr('Error'), self.tr('New password and confirmation do not match.'))
                return None
            else:
                # change PW logic should be implemented here
                self.usrRec.set_password(newPW)
                Repository(get_cMenu_sessionmaker(), User).update(self.usrRec)
        else:
            return None
    # exec_CM_MItm

    def is_newpw_eq_confirm(self) -> bool | None:
        newPW = self.pw_new.text()
        newPW_confirm = self.pw_new_confirm.text()
        if newPW == '' or newPW_confirm == '':
            return None     # not ready to compare if both not given yet
        return newPW == newPW_confirm
    
    def enableOKButton(self):
        if not self.dlgButtons:
            return
        all_pwInfo_given = all([
            self.pw_old.text() != '' or not self.required_oldPW == True,   # if old PW is required, it must be given; if not required, it's ok to be empty
            self.pw_new.text() != '',
            self.pw_new_confirm.text() != '',
            self.is_newpw_eq_confirm() == True,
        ])
        self.dlgButtons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(all_pwInfo_given)
    # enableOKButton

    def check_pwnew_confirm(self):
        if self.is_newpw_eq_confirm() == False:
            QMessageBox.warning(self, self.tr('Warning'), self.tr('New password and confirmation do not match.'))
        self.enableOKButton()
    # check_pwnew_confirm
    
    