from sqlalchemy.orm import (DeclarativeBase, Mapped, mapped_column, relationship, Session, )
from sqlalchemy import (Column, Integer, MetaData, String, Boolean, ForeignKey, SmallInteger, UniqueConstraint, inspect, )


ix_naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
ix_metadata_obj = MetaData(naming_convention=ix_naming_convention)

class UserBase(DeclarativeBase):
    """
    This provides default implementations for the methods that Flask-Login
    expects user objects to have.
    """
    __abstract__ = True
    metadata = ix_metadata_obj

    # Python 3 implicitly set __hash__ to None if we override __eq__
    # We set it back to its default implementation
    __hash__ = object.__hash__

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return self.is_active

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return str(self.id)     #type: ignore
        except AttributeError:
            raise NotImplementedError("No `id` attribute - override `get_id`") from None

    def __eq__(self, other):
        """
        Checks the equality of two `UserMixin` objects using `get_id`.
        """
        if isinstance(other, UserBase):
            return self.get_id() == other.get_id()
        return NotImplemented

    def __ne__(self, other):
        """
        Checks the inequality of two `UserMixin` objects using `get_id`.
        """
        equal = self.__eq__(other)
        if equal is NotImplemented:
            return NotImplemented
        return not equal


class AnonymousUserBase(DeclarativeBase):
    """
    This is the default object for representing an anonymous user.
    """
    __abstract__ = True
    metadata = ix_metadata_obj

    @property
    def is_authenticated(self):
        return False

    @property
    def is_active(self):
        return False

    @property
    def is_anonymous(self):
        return True

    def get_id(self):
        return


class User(UserBase):   
    """
    User model for authentication with database columns.
    Inherit from UserMixin to get default implementations for:
    - is_authenticated, is_active, is_anonymous, get_id()
    """
    __bind_key__ =  cTools_bind_key
    __tablename__ = cTools_tablenames.get('User', 'users')

    id:Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username:Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    first_name:Mapped[str] = mapped_column(String(80), nullable=False)
    last_name:Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    email:Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    password_optional:Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    password_hash:Mapped[str] = mapped_column(String(255), nullable=False)
    active_status:Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser:Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    permissions:Mapped[str] = mapped_column(String(1024), nullable=False, default='')
    menuGroup:Mapped[int] = mapped_column(Integer, ForeignKey(menuGroups.id), nullable=True)
    date_joined:Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    last_login:Mapped[datetime] = mapped_column(DateTime, nullable=True)

    @property
    def is_active(self):
        return self.active_status
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the hash."""
        verdict = check_password_hash(self.password_hash, password)
        return verdict

    def has_permission(self, permission_name: str) -> bool:
        """Check if the user has a specific permission."""
        if self.is_superuser:
            return True  # Superusers have all permissions
        permissions_list = self.permissions.lower().split(',') if self.permissions else []
        return permission_name.lower() in permissions_list

    def update_last_login(self):
        """Update the last login timestamp."""
        self.last_login = datetime.now()
        db_instance.session.commit()

    def __repr__(self):
        return f'<User {self.username}>'

    def __init__(self, **kw: Any):
        """Initialize a user instance."""
        inspector = inspect(db_instance.engine)
        if not inspector.has_table(self.__tablename__):
            # If the table does not exist, create it
            db_instance.create_all()
        super().__init__(**kw)
# User
