from functools import wraps

from . import current_user
from .notify import (
    uauth_notify_mustlogin,
    uauth_notify_nopermission,
    uauth_notify_inactive,
    uauth_notify_mustbeanon,
    )

# ============================================================================
# CUSTOM DECORATORS
# ============================================================================

def login_required(func):
    """
    If you decorate a view with this, it will ensure that the current user is
    logged in and authenticated before calling the actual view. (If they are
    not, it calls the :attr:`LoginManager.unauthorized` callback.) For
    example::

        @app.route('/post')
        @login_required
        def post():
            pass

    If there are only certain times you need to require that your user is
    logged in, you can do so with::

        if not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()

    ...which is essentially the code that this function adds to your views.

    .. Note ::

        Per `W3 guidelines for CORS preflight requests
        <http://www.w3.org/TR/cors/#cross-origin-request-with-preflight-0>`_,
        HTTP ``OPTIONS`` requests are exempt from login checks.

    :param func: The view function to decorate.
    :type func: function
    """

    @wraps(func)
    def decorated_view(*args, **kwargs):
        cUsr = current_user()
        if cUsr is None or not cUsr.is_authenticated:
            return uauth_notify_mustlogin()
        return func(*args, **kwargs)

    return decorated_view

# def login_required_custom(f):
#     """
#     Custom decorator to restrict views to authenticated users only.
#     This is in addition to Flask-Login's @login_required decorator.
#     Use this if you want custom behavior. 
#     """
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if not current_user.is_authenticated:
#             flash('You must be logged in to access this page.', 'warning')
#             return redirect(url_for('auth.login', next=request.url))
#         return f(*args, **kwargs)
#     return decorated_function


def superuser_required(f):
    """
    Decorator to restrict views to superusers only.
    Similar to Django's @permission_required decorator.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        cUsr = current_user()
        if cUsr is None or not cUsr.is_authenticated:
            return uauth_notify_mustlogin()
        
        if not cUsr.is_superuser:
            return uauth_notify_nopermission()
        
        return f(*args, **kwargs)
    return decorated_function


def active_user_required(f):
    """
    Decorator to ensure the user account is active.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        cUsr = current_user()
        if cUsr is None or not cUsr.is_authenticated:
            return uauth_notify_mustlogin()
        
        if not cUsr.is_active:
            return uauth_notify_inactive()
        
        return f(*args, **kwargs)
    return decorated_function


def anonymous_required(f):
    """
    Decorator to restrict views to non-authenticated users only.
    Useful for login/register pages.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        cUsr = current_user()
        if cUsr is not None and cUsr.is_authenticated:
            return uauth_notify_mustbeanon()

        return f(*args, **kwargs)
    return decorated_function

