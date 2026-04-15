from functools import wraps

from . import current_user

# ============================================================================
# CUSTOM DECORATORS
# ============================================================================

def login_required_custom(f):
    """
    Custom decorator to restrict views to authenticated users only.
    This is in addition to Flask-Login's @login_required decorator.
    Use this if you want custom behavior. 
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('You must be logged in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def superuser_required(f):
    """
    Decorator to restrict views to superusers only.
    Similar to Django's @permission_required decorator.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated: 
            flash('You must be logged in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        
        if not current_user.is_superuser:
            flash('You do not have permission to access this page. ', 'danger')
            abort(403)  # Forbidden
        
        return f(*args, **kwargs)
    return decorated_function


def active_user_required(f):
    """
    Decorator to ensure the user account is active.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('You must be logged in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        
        if not current_user.is_active:
            logout_user()
            flash('Your account has been deactivated.  Please contact support.', 'danger')
            return redirect(url_for('auth.login'))
        
        return f(*args, **kwargs)
    return decorated_function


def anonymous_required(f):
    """
    Decorator to restrict views to non-authenticated users only.
    Useful for login/register pages.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

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
        if request.method in EXEMPT_METHODS:
            pass
        elif not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()

        # flask 1.x compatibility
        # current_app.ensure_sync is only available in Flask >= 2.0
        if callable(getattr(current_app, "ensure_sync", None)):
            return current_app.ensure_sync(func)(*args, **kwargs)
        return func(*args, **kwargs)

    return decorated_view


def fresh_login_required(func):
    """
    If you decorate a view with this, it will ensure that the current user's
    login is fresh - i.e. their session was not restored from a 'remember me'
    cookie. Sensitive operations, like changing a password or e-mail, should
    be protected with this, to impede the efforts of cookie thieves.

    If the user is not authenticated, :meth:`LoginManager.unauthorized` is
    called as normal. If they are authenticated, but their session is not
    fresh, it will call :meth:`LoginManager.needs_refresh` instead. (In that
    case, you will need to provide a :attr:`LoginManager.refresh_view`.)

    Behaves identically to the :func:`login_required` decorator with respect
    to configuration variables.

    .. Note ::

        Per `W3 guidelines for CORS preflight requests
        <http://www.w3.org/TR/cors/#cross-origin-request-with-preflight-0>`_,
        HTTP ``OPTIONS`` requests are exempt from login checks.

    :param func: The view function to decorate.
    :type func: function
    """

    @wraps(func)
    def decorated_view(*args, **kwargs):
        if request.method in EXEMPT_METHODS:
            pass
        elif not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        elif not login_fresh():
            return current_app.login_manager.needs_refresh()
        try:
            # current_app.ensure_sync available in Flask >= 2.0
            return current_app.ensure_sync(func)(*args, **kwargs)
        except AttributeError:  # pragma: no cover
            return func(*args, **kwargs)

    return decorated_view

