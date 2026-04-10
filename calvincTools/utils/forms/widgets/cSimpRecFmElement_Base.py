from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget


class cSimpRecFmElement_Base(QWidget):
    """Base class for form elements in simple record forms.

    This abstract base class defines the interface that all form elements must implement
    for loading from and saving to ORM records, as well as tracking dirty state.

    Signals:
        signalFldChanged: Emitted when the field value changes.
        dirtyChanged: Emitted when the dirty state changes.
    """
    signalFldChanged: Signal = Signal(object)
    dirtyChanged = Signal(bool)

    def loadFromRecord(self, rec: object) -> None:
        """Fill widget from ORM record.

        Args:
            rec: ORM record object to load data from.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError

    def saveToRecord(self, rec: object) -> None:
        """Push widget state into ORM record.

        Args:
            rec: ORM record object to save data to.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError

    def isDirty(self) -> bool:
        """Return True if the widget's value differs from what was loaded.

        Returns:
            bool: True if the value has been modified, False otherwise.
        """
        return False

    def setDirty(self, dirty: bool = True, sendSignal:bool = True) -> None:
        """Mark the field/subform as dirty.

        Args:
            dirty (bool, optional): Whether to mark as dirty. Defaults to True.
            sendSignal (bool, optional): Whether to emit dirtyChanged signal. Defaults to True.
        """
        pass
# endclass cSimpRecFmElement_Base
    def endofclass(self):
        pass