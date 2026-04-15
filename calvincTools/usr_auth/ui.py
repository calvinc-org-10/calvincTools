from typing import (
    Any, List, Type, Text, 
)

from PySide6.QtCore import (Qt, QObject, Signal, )
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QWidget, 
    QLabel, QLineEdit, QTextEdit,
    QPushButton,
    )

from sqlalchemy.orm import Session, sessionmaker

from calvincTools.database import (get_cMenu_sessionmaker, Repository, )
from calvincTools.utils.forms import (cSRFSingleRecordForm, cQFormFieldDef)
from calvincTools.utils.forms.definitions.cQFormLayout import cQFormLayout

from .auth import MiniAuth
from .models import User


class LoginForm(cSRFSingleRecordForm):
    """
    Form for login page.
    """
    # _formname = 'Login Form'
    _ORMmodel = User
    _ssnmaker = get_cMenu_sessionmaker()
    
    login_successful = Signal()
    
    
    def __init__(self, 
        formname: str|None = None,
        logo: QPixmap|None = None,
        retries: int = 3,
        field_defs: List[cQFormFieldDef] | None = None,
        model: Type[Any]|None = None,
        ssnmaker: sessionmaker[Session] | None = None,
        parent: QWidget | None = None,
        *args, **kwds: Any
        ) -> None:
        
        self._logo = logo
        self._retries = retries
        self._numtries = 0
        
        super().__init__(
            formname=formname,
            field_defs=field_defs,
            model=model,
            ssnmaker=ssnmaker,
            parent=parent,
            *args, **kwds
            )
    
        
    def _buildFormLayout(self) -> cQFormLayout:
        layouts = super()._buildFormLayout()
        
        # add elements to the layout
        if self._logo is not None:
            pixmap = self._logo
            logo_label = QLabel()
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layouts.main.insertWidget(0, logo_label, alignment=Qt.AlignmentFlag.AlignCenter)
            
        return layouts
    
    def defineFields(self):
        flds = [
            cQFormFieldDef(
                name='loginmsg',
                field_type=cQFormFieldDef.cQFormFieldType.INTERNAL,
                label=' ',
                position=(0, 0),
                widget_type=QLabel,
            ),
            cQFormFieldDef(
                name='username', 
                label='Username', 
                widget_type=QLineEdit,
                position=(1,0)
                ),
            cQFormFieldDef(
                name='password', 
                label='Password', 
                widget_type=QLineEdit,
                position=(2,0),
                ),
            cQFormFieldDef(
                name='login', 
                field_type=cQFormFieldDef.cQFormFieldType.INTERNAL,
                label='Login', 
                position=(4,0),
                widget_type=QPushButton,
                on_change=self._on_login_clicked
            ),
            cQFormFieldDef(
                name='greeting',
                field_type=cQFormFieldDef.cQFormFieldType.INTERNAL,
                label=' ',
                position=(6,0),
                widget_type=QLabel,
            ),
            cQFormFieldDef(
                name='appnews',
                field_type=cQFormFieldDef.cQFormFieldType.INTERNAL,
                label=' ',
                position=(0, 1, 7, 1),
                widget_type=QTextEdit,
                readonly=True,
            ),
        ]
        
        return flds

    def _build_fields(self):
        flds = super()._build_fields()
        
        # set text color of login failure message to red
        loginmsgfld = self._formWidgets.get('loginmsg')
        if loginmsgfld is not None:
            widg = loginmsgfld.widget
            widg.setStyleSheet("color: red;")  # type: ignore
        
        # set password field to Password mode
        pwfld = self._formWidgets.get('password')
        if pwfld is not None:
            widg = pwfld.widget
            widg.setEchoMode(QLineEdit.EchoMode.Password)   # type: ignore
            widg.setPlaceholderText('Enter your password')  # type: ignore
        
        # set appnews background transparent and remove border to make it look more like a label than an edit box
        appnewsfld = self._formWidgets.get('appnews')
        if appnewsfld is not None:
            widg = appnewsfld.widget
            widg.setStyleSheet("background: transparent; border: none;")  # type: ignore
        
        return flds
        
    def defineActionButtons(self):
        return []

    def showNewRecordFlag(self) -> None:
        # no, let's not
        return 
    
    def initialdisplay(self):
        """
        Initializes a new record and displays it in the form. Also performs any necessary setup for the initial display of the form.
        """
        self.initializeRec()
    # initialdisplay()

    def _on_login_clicked(self):
        """Handle login button click event."""
        """Perform login logic. Return True if successful, False otherwise."""
        from . import current_user

        uname = self._formWidgets.get('username').get_value()   # type: ignore
        usrRec = self.userRecord(uname)
        if usrRec is None:
            self.try_again()
            return
        pw = self._formWidgets.get('password').get_value()     # type: ignore
        if self.verify_user(uname, pw):
            self._formWidgets.get('greeting').set_value(f"Welcome, {usrRec.first_name}!")  # type: ignore
            self._formWidgets.get('loginmsg').set_value("")  # type: ignore
            current_user = usrRec
            # log the login time
            usrRec.update_last_login()
            # emit signal or call callback to indicate successful login, if needed
            self.login_successful.emit()
            return
        self.try_again()
    # on_login_clicked
    
    def try_again(self):
        generic_fail_msg = "Login failed. Please check your username and password and try again."
        self._numtries += 1
        if self._numtries >= self._retries:
            self._formWidgets.get('loginmsg').set_value("Maximum login attempts exceeded. Please try again later.")  # type: ignore
            # disable login button
            login_btn = self._formWidgets.get('login').widget  # type: ignore
            login_btn.setEnabled(False)  # type: ignore
            
            # better yet, close the form and require reopening to try again, which will reset the retry count and re-enable the button
            self.close()
        else:
            self._formWidgets.get('loginmsg').set_value(generic_fail_msg)  # type: ignore
        # endif retries
    # try_again
    
    def login(self, username: str, password: str) -> bool:
        """Perform login logic. Return True if successful, False otherwise."""
        # Placeholder for actual authentication logic
        return False

    def reset_fields(self):
        # This one-liner clears the text and moves focus back to the username
        interactive_fields = ['username', 'password']
        [field.set_value('') for field in [self._formWidgets[FFF] for FFF in interactive_fields]]    # type: ignore
        self._formWidgets['username'].widget.setFocus()

    def userRecord(self, username):
        # type: (Text) -> Any
        modl = self.ORMmodel()
        ssnmkr = self.ssnmaker()
        assert modl is not None and ssnmkr is not None, "ORM model and sessionmaker must be defined"
        
        userwhere = self.ORMmodel().username == username    # type: ignore
        userRecs = Repository(ssnmkr, modl).get_all(userwhere)
        if userRecs is not None and len(userRecs) > 0:
            return userRecs[0]
        return None

    def verify_user(self, username, password):
        """
        verify that the password presented for the user is actually the passwoprd stored
        returns True if the password is correct or if password_optional=True for the user,
            False if not or if the user doesn't exist

        Args:
            username (_type_): _description_
            password (_type_): _description_

        Returns:
            _type_: _description_
        """
        # Placeholder for actual authentication logic
        # For example, you could query the database for the user and check the password hash
        usrRec = self.userRecord(username)
        if usrRec is not None:
            if not usrRec.is_active:
                return False
            if usrRec.password_optional:
                return True
            # TODO: start bringing MiniAuth in here - that module duplicates a lot of db touches.
            miniAuth = MiniAuth(self.ORMmodel(), self.ssnmaker())
            return miniAuth.verify_user(usrRec.username,  password)
        return False
