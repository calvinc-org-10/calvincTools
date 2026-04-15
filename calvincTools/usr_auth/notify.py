"""
"""
from PySide6.QtWidgets import (QMessageBox, )

def uauth_notify_base(parent, message, title='Notification'):
    """Display a notification message box to the user.
    
    Args:
        parent: Parent widget for the message box.
        message: Message to display to the user.
        title: Title of the message box (default is 'Notification').
    """
    msg = QMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.setText(message)
    msg.open()

def uauth_notify_mustlogin(parent=None, message="You must be logged in to perform this action."):
    """Display a notification that the user must log in to perform an action."""
    uauth_notify_base(parent, message, title="Login Required")

def uauth_notify_nopermission(parent=None, message="You must have permission to perform this action."):
    """Display a notification that the user must log in to perform an action."""
    uauth_notify_base(parent, message, title="Permission Required")
    
def uauth_notify_inactive(parent=None, message='Your account has been deactivated.  Please contact support.'):
    """Display a notification that the user must log in to perform an action."""
    uauth_notify_base(parent, message, title="DeActivated Account")
    
def uauth_notify_mustbeanon(parent=None, message='This action is only available to anonymous users. Please log out to perform this action.'):
    """Display a notification that the user must log in to perform an action."""
    uauth_notify_base(parent, message, title="Anonymous User Required")
    

