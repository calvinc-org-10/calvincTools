from .models import User        # import User first to avoid circular dependencies, as User is used in other modules in this package
from .ui import LoginForm

_current_user: User|None = None

def current_user() -> User|None:
    global _current_user
    return _current_user
def set_current_user(user: User):
    global _current_user
    _current_user = user
