from typing import (
    Any, List, Type
)

from PySide6.QtCore import Qt, QObject
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QWidget, 
    QLabel, QLineEdit, QTextEdit,
    QPushButton,
    )

from sqlalchemy.orm import Session, sessionmaker

from calvincTools.database import get_cMenu_sessionmaker
from calvincTools.utils.forms import (cSRFSingleRecordForm, cQFormFieldDef)
from calvincTools.utils.forms.definitions.cQFormLayout import cQFormLayout

from .models import User


class LoginForm(cSRFSingleRecordForm):
    """
    Form for login page.
    """
    # _formname = 'Login Form'
    _ORMmodel = User
    _ssnmaker = get_cMenu_sessionmaker()
    
    
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
        
    def _on_login_clicked(self):
        """Handle login button click event."""
        """Perform login logic. Return True if successful, False otherwise."""
        # Placeholder for actual authentication logic
        # send signal to parent or main app to indicate login attempt
        print("Login button clicked")
        pass
    
    def login(self, username: str, password: str) -> bool:
        """Perform login logic. Return True if successful, False otherwise."""
        # Placeholder for actual authentication logic
        return False
