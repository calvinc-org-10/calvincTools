from .models import User        # import User first to avoid circular dependencies, as User is used in other modules in this package
from .ui import LoginForm

current_user: User|None = None
