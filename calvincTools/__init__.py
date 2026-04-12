from .__version__ import (
    _pkgname,
    _ver_date,
    _base_ver_major, _base_ver_minor, _base_ver_patch, _base_ver, 
    __version__, sysver, sysver_key,
    __author__, __email__, 
    )

# Import main modules here as needed
# from .module import function

from .apphooks import cTools_apphooks

def calvincTools_init(usr_auth: bool,
    app_sessionmaker=None, 
    FormNameToURL_Map={},
    ExternalWebPageURL_Map={},
    appver='',
    **kwargs
    ):
    """
    Initialize calvincTools
    Pass in structures that calvincTools will need which are cntrolled by calling app

    Returns:
        None
    """
    ## dirty little secret: this started life as calvincTools_apphooks, but I wanted to add some more app-specific initialization here.
    ## so I renamed it to calvincTools_init, but calvincTools_apphooks still exists and still does the heavy lifting. 
    ## However, I want to keep the apphooks separate from the main initialization, so that they can be used independently if needed.
    ## apps should call calvincTools_init, not calvincTools_apphooks, but calvincTools_init will call calvincTools_apphooks.initialize to set up the hooks.

    # Initialize app hooks - this is the main point of this function, to ensure that the hooks are set up before any
    cTools_apphooks.initialize(
        app_sessionmaker=app_sessionmaker, 
        FormNameToURL_Map=FormNameToURL_Map,
        ExternalWebPageURL_Map=ExternalWebPageURL_Map,
        appver=appver,
        **kwargs
    )
    
    # login, if usr_auth is True
    if usr_auth:
        ...
        # init_login_manager(app)
            
        # Create default Calvin user if not exists
        # R E M O V E   I N   P R O D U C T I O N   ! ! !
        # create_calvin(app)
    
    # implement later
    # cTools_tables = (None, None, None, None, None)   # will be set by init_cDatabase
    # cTools_bind_key=None, 
    # cTools_tablenames=None, 
    # cTools_models=None):
        # from .models import init_cDatabase      # can I move this back to main imports?
        # self.cTools_tables = init_cDatabase(app, app_db, cTools_bind_key, cTools_tablenames, cTools_models)

# calvinCTools_init

