# calvinctools/apphooks.py

class cTools_apphooks:
    """
    A Singleton class to hold application-specific hooks and resources
    for the calvinctools toolkit, such as database sessionmakers.

    This acts as a Service Locator for external dependencies.
    """
    _instance = None
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

    def __new__(cls):
        # Implement the Singleton pattern: always return the same instance
        if cls._instance is None:
            cls._instance = super(cTools_apphooks, cls).__new__(cls)
        return cls._instance

    @classmethod
    def initialize(cls, 
            app_sessionmaker=None, 
            FormNameToURL_Map={},
            ExternalWebPageURL_Map={},
            appname='Application',
            appver='',
            logo=None,
            **kwargs
            ):
        """
        The main method to initialize the singleton with all required hooks.
        This should be called ONCE during application startup before
        any calvinctools module is used.
        """
        instance = cls() # This ensures the instance exists
        if app_sessionmaker is not None:
            instance.app_sessionmaker = app_sessionmaker
        if FormNameToURL_Map:
            instance.FormNameToURL_Map = FormNameToURL_Map
        if ExternalWebPageURL_Map:
            instance.ExternalWebPageURL_Map = ExternalWebPageURL_Map
        if appver:
            instance.appver = appver
        if appname:
            instance.appname = appname
        if logo:
            instance.logo = logo
                    
        # You can add other app-specific resources here
        # Example: instance._external_config = kwargs.get('config')
        
        return instance
    # initialize
    @classmethod
    def is_initialized(cls):
        """
        Check if all required hooks have been initialized.
        """
        instance = cls()
        return not any(getattr(instance, f'_{attr}', None) is None for attr in cls._MUSTBEINITIALIZED)
    # is_initialized

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
            
    # Additional getters/setters can be added as needed

# Convenience function to get the instance
def get_apphooks():
    """
    Global access point to the initialized cTools_apphooks instance.
    """
    return cTools_apphooks()