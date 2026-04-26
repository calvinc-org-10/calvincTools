
from PySide6.QtCore import (QObject, Signal, Slot, )
from PySide6.QtWidgets import (QStackedWidget, )

from .usr_auth import (LoginForm, current_user, set_current_user, )
from .usr_auth.models import User_usrauth_not_used

from .cMenu import cMenu

class calvincTools(QObject):
    """
    A Singleton class to hold application-specific hooks and resources
    for the calvinctools toolkit, such as database sessionmakers.

    This acts as a Service Locator for external (and some internal) dependencies.
    """
    _instance = None
    _initialized = False  # Track if initialization has occurred
    
    _usr_auth = None            # is the usr_auth module being used, or is there no logging in?
    _main_window_stack = None   # reference to the main window's QStackedWidget, for use in navigation between "main" forms (cMenu, FormLogin) 
    _login_form = None          # reference to the login form, for use in logout functionality (to return to login form after logout)
    _menu_form = None           # reference to the menu form, for use in logout functionality (to reset menu form to default state on logout)
    
    _app_sessionmaker = None
    _appver = ''
    _FormNameToURL_Map = {}
    _ExternalWebPageURL_Map = {}
    _appname='Application'
    _logo=None
    _MUSTBEINITIALIZED: set = {
        'app_sessionmaker',
        'FormNameToURL_Map', 
        'ExternalWebPageURL_Map',
        }
    
    LogoutRequested    = Signal()  # Signal to indicate logout has been requested
    Logout             = Signal()  # Signal to indicate logout has been initiated (after any necessary cleanup)
    ShutdownRequested  = Signal()  # Signal to indicate shutdown has been requested
    Shutdown           = Signal()  # Signal to indicate shutdown has been initiated (after any necessary cleanup)

    def __new__(cls, *args, **kwargs):
        # Implement the Singleton pattern: always return the same instance
        if cls._instance is None:
            cls._instance = super(calvincTools, cls).__new__(cls)
            # Initialize QObject parent class
            super(calvincTools, cls._instance).__init__()
        return cls._instance

    def __init__(self, 
            app_sessionmaker=None, 
            FormNameToURL_Map=None,
            ExternalWebPageURL_Map=None,
            usr_auth=None,
            appname=None,
            appver=None,
            logo=None,
            **kwargs
            ):
        """
        Initialize the singleton with all required hooks.
        This only runs once, on first instantiation. Subsequent calls are ignored.
        """
        # Only initialize once - use simple flag to avoid recursion
        if self.__class__._initialized:
            return
        
        # Set provided values, or keep class defaults
        if app_sessionmaker is not None:
            self._app_sessionmaker = app_sessionmaker
        self._FormNameToURL_Map = FormNameToURL_Map or {}
        self._ExternalWebPageURL_Map = ExternalWebPageURL_Map or {}
        self._appver = appver or ''
        self._appname = appname or 'Application'
        if logo is not None:
            self._logo = logo
        
        # Mark as initialized and validate required fields were set
        self.__class__._initialized = True
        
        # Now validate that all required fields are properly initialized
        if not self.__class__.is_properly_initialized():
            # Reset initialization flag so they can try again
            self.__class__._initialized = False
            missing = [attr for attr in self._MUSTBEINITIALIZED 
                      if getattr(self, f'_{attr}', None) is None]
            raise RuntimeError(
                f"calvincTools initialization incomplete. Missing required fields: {missing}. "
                f"Please provide: {', '.join(missing)}"
            )
        # endif not properly initialized
        
        # set other hooks that aren't required but may be used by the app
        self.usr_auth = usr_auth # use the setter to ensure it's set to a boolean (defaulting to True if usr_auth is provided but not a bool)
        
        self.create_main_window_stack()  # create the main window stack and its forms (login, menu) at initialization so they're ready to go when needed
        
    # __init__

    @classmethod
    def is_properly_initialized(cls):
        """
        Check if all required hooks have been initialized.
        Returns True only if the instance exists, is marked as initialized,
        and all required fields are set.
        """
        # Check if instance exists and is marked as initialized
        if cls._instance is None or not cls._initialized:
            return False
        
        # Check if all required fields are set (not None)
        return not any(getattr(cls._instance, f'_{attr}', None) is None 
                      for attr in cls._MUSTBEINITIALIZED)
    # is_properly_initialized

    @property
    def app_sessionmaker(self):
        """
        Retrieve the configured application database sessionmaker.
        """
        if self._app_sessionmaker is None:
            raise RuntimeError(
                "cTools_apphooks has not been initialized with 'app_sessionmaker'. "
                "Call cTools_apphooks.initialize() first."
            )
        return self._app_sessionmaker
    # get_app_sessionmaker
    @app_sessionmaker.setter
    def app_sessionmaker(self, app_sessionmaker):
        """
        Set the application database sessionmaker.
        """
        self._app_sessionmaker = app_sessionmaker
    # set_app_sessionmaker

    @property
    def appver(self):
        return self._appver
    @appver.setter
    def appver(self, appver):
        self._appver = appver

    @property
    def FormNameToURL_Map(self):
        if self._app_sessionmaker is None:
            raise RuntimeError(
                "cTools_apphooks has not been initialized with 'FormNameToURL_Map'. "
                "Call cTools_apphooks.initialize() first."
            )
        return self._FormNameToURL_Map
    @FormNameToURL_Map.setter
    def FormNameToURL_Map(self, FormNameToURL_Map):
        self._FormNameToURL_Map = FormNameToURL_Map

    @property
    def ExternalWebPageURL_Map(self):
        if self._app_sessionmaker is None:
            raise RuntimeError(
                "cTools_apphooks has not been initialized with 'ExternalWebPageURL_Map'. "
                "Call cTools_apphooks.initialize() first."
            )
        return self._ExternalWebPageURL_Map
    @ExternalWebPageURL_Map.setter
    def ExternalWebPageURL_Map(self, ExternalWebPageURL_Map):
        self._ExternalWebPageURL_Map = ExternalWebPageURL_Map

    @property
    def appname(self):
        return self._appname
    @appname.setter
    def appname(self, appname):
        self._appname = appname

    @property
    def logo(self):
        return self._logo
    @logo.setter
    def logo(self, logo):
        self._logo = logo

    @property
    def usr_auth(self):
        return self._usr_auth
    @usr_auth.setter
    def usr_auth(self, usr_auth):
        self._usr_auth = usr_auth if isinstance(usr_auth, bool) else True  # if usr_auth is provided and is a bool, use it; otherwise default to True (using usr_auth)            

    def main_window_stack(self):
        return self._main_window_stack
    def login_form(self):
        return self._login_form
    def menu_form(self):
        return self._menu_form

    def create_main_window_stack(self):
        self._login_form = LoginForm(
            formname=self.appname + " Login",
            logo=self.logo,
            # retries=self.retries,
            appver=self.appver,
            )
        self.login_form().login_successful.connect(self._on_login_successful)    # type: ignore
        
        self._menu_form = cMenu(
            parent=None,
            # logo=self.logo,
            )
        
        self._main_window_stack = QStackedWidget()
        if self._login_form is not None:
            self._main_window_stack.addWidget(self._login_form)
        if self._menu_form is not None:
            self._main_window_stack.addWidget(self._menu_form)
            
    # create_main_window_stack
    
    def show_menu_form(self):
        MFm = self.menu_form()
        # When login is successful, navigate to the menu form
        if self._main_window_stack is None or MFm is None:
            return  # main window stack or menu form not properly initialized, can't navigate
        self._main_window_stack.setCurrentWidget(MFm)
        cUsr = current_user()
        mGroup = cMenu._DFLT_menuGroup if cUsr is None else cUsr.menuGroup
        MFm.loadMenu(mGroup)
    # show_menu_form
    def show_login_form(self):
        LFm = self.login_form()
        if self._main_window_stack is None or LFm is None:
            return  # main window stack or menu form not properly initialized, can't navigate
        if self.usr_auth:
            LFm.reset_fields() # reset login form fields (e.g. clear username/password) when showing login form
            self._main_window_stack.setCurrentWidget(LFm)
        else:
            self.ShutdownRequested.emit()  # emit logout requested signal to trigger any necessary cleanup in the app (e.g. clearing user session data) when showing login form if usr_auth is False (i.e. no login form, so just trigger logout process)
            return
    # show_login_form
    
    @Slot()
    def _on_login_successful(self):
        self.show_menu_form()
    # on_login_successful
    
    def login(self):
        # Show the login form or the menu form (whichever is appropriate based on self.usr_auth) when the application starts
        LFm = self.login_form()
        MFm = self.menu_form()
        if self._main_window_stack is None or LFm is None:
            return  # main window stack or menu form not properly initialized, can't navigate
        if self.usr_auth:
            self.show_login_form()
        else:
            if MFm is None:
                return
            set_current_user(User_usrauth_not_used)  # set to dummy user since we're not using authentication
            self.show_menu_form()
            
    # implement later (???)
    # cTools_tables = (None, None, None, None, None)   # will be set by init_cDatabase
    # cTools_bind_key=None, 
    # cTools_tablenames=None, 
    # cTools_models=None):
        # from .models import init_cDatabase      # can I move this back to main imports?
        # self.cTools_tables = init_cDatabase(app, app_db, cTools_bind_key, cTools_tablenames, cTools_models)

# calvinCTools_init
    def end_of_class(self):
        pass
