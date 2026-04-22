"""
"""
from PySide6.QtWidgets import (QApplication, QMessageBox, )

def uauth_notify(message, title='Notification', parent=None):
    """Display a notification message box to the user.
    
    Args:
        parent: Parent widget for the message box.
        message: Message to display to the user.
        title: Title of the message box (default is 'Notification').
    """
    parent = parent or QApplication.activeWindow()
    
    msg = QMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.setText(message)
    msg.open()

def uauth_notify_mustlogin(message="You must be logged in to perform this action.", parent=None):
    """Display a notification that the user must log in to perform an action."""
    uauth_notify(message, title="Login Required", parent=parent)

def uauth_notify_nopermission(message="You must have permission to perform this action.", parent=None):
    """Display a notification that the user must log in to perform an action."""
    uauth_notify(message, title="Permission Required", parent=parent)
    
def uauth_notify_inactive(message='Your account has been deactivated.  Please contact support.', parent=None):
    """Display a notification that the user must log in to perform an action."""
    uauth_notify(message, title="DeActivated Account", parent=parent)
    
def uauth_notify_mustbeanon(message='This action is only available to anonymous users. Please log out to perform this action.', parent=None):
    """Display a notification that the user must log in to perform an action."""
    uauth_notify(message, title="Anonymous User Required", parent=parent)
    

