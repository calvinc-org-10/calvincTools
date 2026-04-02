# TODO: implement editing
# deprecate? see subform widget 
from calvincTools.utils.cQModels import SQLAlchemyTableModel
from calvincTools.utils.forms.cQFmNameLabel import cQFmNameLabel


from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QHeaderView, QPushButton, QTableView, QVBoxLayout, QWidget
from sqlalchemy.orm import Session, sessionmaker


from typing import Any, Type


class cSimpleTableForm(QWidget):
    """A simple form for displaying and editing a database table.

    This widget provides a basic table view with add and save functionality
    for SQLAlchemy ORM models.

    Attributes:
        _tbl: The SQLAlchemy ORM model class.
        _formname: Name of the form.
        _ssnmaker: Session maker for database connections.
        model: The SQLAlchemyTableModel backing the table view.
    """
    _tbl = None
    _formname = None
    _ssnmaker: sessionmaker[Session]

    # TODO: pass in sessionmaker
    def __init__(self,
        formname: str|None = None,
        tbl: Type[Any]|None = None,
        ssnmaker = None,
        parent: QWidget|None = None
        ):
        """Initialize the SimpleTableForm.

        Args:
            formname (str): The name of the form.
            tbl (Type[Any]): The SQLAlchemy model class for the table.
            parent (QWidget | None, optional): The parent widget. Defaults to None.
        """
        super().__init__(parent)

        if formname:
            self._formname = formname
        if tbl:
            self._tbl = tbl
        if ssnmaker:
            self._ssnmaker = ssnmaker

        # Layout
        layoutForm = QVBoxLayout(self)

        layoutFormHdr = QHBoxLayout()
        lblFormName = cQFmNameLabel(parent=self)
        lblFormName.setText(self.tr(str(self._formname)))
        layoutFormHdr.addWidget(lblFormName)
        self.setWindowTitle(self.tr(str(self._formname)))

        # Setup model
        assert self._tbl, "Table model class must be provided"
        assert ssnmaker, "Session maker must be provided"
        self.model = SQLAlchemyTableModel(self._tbl, ssnmaker)
        # self.model.setEditStrategy(QSqlTableModel.OnFieldChange)

        # Setup view
        layoutFormMain = QGridLayout()
        tableView = QTableView()
        header = tableView.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        # Apply stylesheet to control text wrapping
        tableView.setStyleSheet("""
        QHeaderView::section {
            padding: 5px;
            font-size: 12px;
            text-align: center;
            white-space: normal;  /* Allow text to wrap */
        }
        """)
        tableView.setModel(self.model)
        tableView.setEditTriggers(QTableView.EditTrigger.DoubleClicked | QTableView.EditTrigger.EditKeyPressed)
        rows = tableView.model().rowCount()
        colNames = [tableView.model().headerData(n, Qt.Orientation.Horizontal) for n in range(tableView.model().columnCount())]
        # tableView.resizeColumnsToContents()
        layoutFormMain.addWidget(tableView,0,0)

        # Add a add button
        addrow_button = QPushButton("Add Row")
        addrow_button.clicked.connect(lambda: self.addRow())

        # Add a save button
        save_button = QPushButton("Save Changes")
        save_button.clicked.connect(lambda: self.saveRow())

        layoutButtons = QHBoxLayout()
        layoutButtons.addWidget(addrow_button)
        layoutButtons.addWidget(save_button)

        layoutForm.addLayout(layoutFormHdr)
        layoutForm.addLayout(layoutFormMain)
        layoutForm.addLayout(layoutButtons)
    # __init__

    def addRow(self):
        """Insert a new row at the end of the table."""
        self.model.insertRow(self.model.rowCount())
    # addRow

    def saveRow(self):
        """Save all changes made to the table."""
        self.model.save_changes()
    # saveRow
# endclass cSimpleTableForm
