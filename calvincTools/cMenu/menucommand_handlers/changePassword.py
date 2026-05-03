from calvincTools.usr_auth.chngPW_dlg import chngPW_dlg
from calvincTools.usr_auth.decorators import active_user_required


from PySide6.QtWidgets import QWidget


@active_user_required
class changePassword():
    def __init__(self, parent:QWidget|None = None):
        from calvincTools.usr_auth import current_user
        uRec = current_user()
        pwDlg = chngPW_dlg()
        id = uRec.id if uRec else None
        if id is None:
            return
        pwDlg.exec_chg_PW(id, require_oldPW=True)
    # __init__

    def end_of_class(self):
        """ place this after the all methods and comments in the class, to avoid accidentally leaving out a method or comment when copying/pasting or refactoring code"""
        pass