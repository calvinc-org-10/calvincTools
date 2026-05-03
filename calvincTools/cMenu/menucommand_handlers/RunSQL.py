from typing import Dict, List

from calvincTools.utils import SQLAlchemySQLQueryModel, cExcelFile
from openpyxl import Workbook

from calvincTools.utils.forms.widgets import cQFmNameLabel


from PySide6.QtCore import QObject, Qt, Signal, Slot
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QFileDialog, QFormLayout, QFrame, QHBoxLayout, QHeaderView, QLabel, QPlainTextEdit, QPushButton, QTableView, QTextEdit, QVBoxLayout, QWidget


class QWGetSQL(QWidget):
    runSQL = Signal(str)    # Emitted with the SQL string when run is clicked
    cancel = Signal()       # Emitted when cancel is clicked    

    def __init__(self, parent = None):
        super().__init__(parent)

        font = QFont()
        font.setPointSize(12)
        self.setFont(font)

        self.layoutForm = QVBoxLayout(self)

        # Form Header Layout
        self.layoutFormHdr = QVBoxLayout()

        self.lblFormName = cQFmNameLabel()
        self.lblFormName.setText(self.tr('Enter SQL'))
        self.setWindowTitle(self.tr('Enter SQL'))
        self.layoutFormHdr.addWidget(self.lblFormName)
        self.layoutFormHdr.addSpacing(20)

        # main area for entering SQL
        self.layoutFormMain = QFormLayout()
        self.txtedSQL = QTextEdit()
        self.layoutFormMain.addRow(self.tr('SQL statement'), self.txtedSQL)

        # run/Cancel buttons
        self.layoutFormActionButtons = QHBoxLayout()
        self.buttonRunSQL = QPushButton( QIcon.fromTheme(QIcon.ThemeIcon.Computer), self.tr('Run SQL') )
        self.buttonRunSQL.clicked.connect(self._on_run_sql_clicked)
        self.layoutFormActionButtons.addWidget(self.buttonRunSQL, alignment=Qt.AlignmentFlag.AlignRight)
        self.buttonCancel = QPushButton( QIcon.fromTheme(QIcon.ThemeIcon.WindowClose), self.tr('Cancel') )
        self.buttonCancel.clicked.connect(self._on_cancel_clicked)
        self.layoutFormActionButtons.addWidget(self.buttonCancel, alignment=Qt.AlignmentFlag.AlignRight)

        # generic horizontal lines
        horzline = QFrame()
        horzline.setFrameShape(QFrame.Shape.HLine)
        horzline.setFrameShadow(QFrame.Shadow.Sunken)
        horzline2 = QFrame()
        horzline2.setFrameShape(QFrame.Shape.HLine)
        horzline2.setFrameShadow(QFrame.Shadow.Sunken)

        # status message
        self.lblStatusMsg = QLabel()
        self.lblStatusMsg.setText('\n\n')

        # Hints
        self.lblHints = QPlainTextEdit()
        self.lblHints.setReadOnly(True)

        # read txtHints from file
        hintFile = 'assets/SQLHints.txt'
        try:
            with open(hintFile, 'r', encoding='utf-8') as f:
                txtHints = f.read()
        except Exception:
            txtHints = 'PRAGMA table_list;\nPRAGMA table_xinfo(tablname);'
        self.lblHints.setPlainText(txtHints)

        self.layoutForm.addLayout(self.layoutFormHdr)
        self.layoutForm.addLayout(self.layoutFormMain)
        self.layoutForm.addLayout(self.layoutFormActionButtons)
        self.layoutForm.addWidget(horzline)
        self.layoutForm.addWidget(self.lblStatusMsg)
        self.layoutForm.addWidget(horzline2)
        self.layoutForm.addWidget(self.lblHints)

    def _on_run_sql_clicked(self):
        # Emit the runSQL signal with the text from the editor.
        sql_text = self.txtedSQL.toPlainText()
        self.runSQL.emit(sql_text)

    def _on_cancel_clicked(self):
        # Emit the cancel signal.
        self.cancel.emit()

    def closeEvent(self, event):
        self.cancel.emit()  # Emit the signal
        event.accept()  # Accept the close event (allows the window to close)

    def end_of_class(self):
        """ place this after the all methods and comments in the class, to avoid accidentally leaving out a method or comment when copying/pasting or refactoring code"""
        pass


class QWShowSQL(QWidget):
    ReturnToSQL = Signal()
    closeMe = Signal()
    closeBoth = Signal()

    def __init__(self, qmodel:SQLAlchemySQLQueryModel, parent:QWidget|QObject|None = None):
        if isinstance(parent, QWidget) or parent is None:
            super().__init__(parent)

        # save incoming for future use if needed
        self._qmodel = qmodel
        origSQL = qmodel.query()
        # # rowCount will not return true count if not all rows fetched
        # # no longer true?
        # while qmodel.canFetchMore():
        #     qmodel.fetchMore()
        numrows = qmodel.rowCount()
        colNames = [qmodel.headerData(x,Qt.Orientation.Horizontal) for x in range(qmodel.columnCount())]

        font = QFont()
        font.setPointSize(12)
        self.setFont(font)

        self.layoutForm = QVBoxLayout(self)

        # Form Header Layout
        self.layoutFormHdr = QVBoxLayout()

        self.lblFormName = cQFmNameLabel()
        self.lblFormName.setText(self.tr('SQL Results'))
        self.setWindowTitle(self.tr('SQL Results'))
        self.layoutFormHdr.addWidget(self.lblFormName)

        self.layoutFormSQLDescription = QFormLayout()
        lblOrigSQL = QLabel()
        lblOrigSQL.setText(origSQL)
        lblnRecs = QLabel()
        lblnRecs.setText(f'{numrows}')
        lblcolNames = QLabel()
        lblcolNames.setText(str(colNames))
        self.layoutFormSQLDescription.addRow('SQL Entered:', lblOrigSQL)
        self.layoutFormSQLDescription.addRow('rows affctd:', lblnRecs)
        self.layoutFormSQLDescription.addRow('cols:', lblcolNames)


        # main area for displaying SQL
        self.layoutFormMain = QVBoxLayout()

        resultTable = QTableView()
        # resultTable.verticalHeader().setHidden(True)
        header = resultTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        # Apply stylesheet to control text wrapping
        resultTable.setStyleSheet("""
        QHeaderView::section {
            padding: 5px;
            font-size: 12px;
            text-align: center;
            white-space: normal;  /* Allow text to wrap */
        }
        """)
        resultTable.setModel(qmodel)
        self.layoutFormMain.addWidget(resultTable)

        #  buttons
        self.layoutFormActionButtons = QHBoxLayout()
        self.buttonGetSQL = QPushButton( QIcon.fromTheme(QIcon.ThemeIcon.GoPrevious), self.tr('Back to SQL') )
        self.buttonGetSQL.clicked.connect(self._return_to_sql)
        self.layoutFormActionButtons.addWidget(self.buttonGetSQL, alignment=Qt.AlignmentFlag.AlignRight)
        self.buttonDLResults = QPushButton( QIcon.fromTheme(QIcon.ThemeIcon.DocumentSave), self.tr('D/L Results') )
        self.buttonDLResults.clicked.connect(self.DLResults)
        self.layoutFormActionButtons.addWidget(self.buttonDLResults, alignment=Qt.AlignmentFlag.AlignRight)
        self.buttonCancel = QPushButton( QIcon.fromTheme(QIcon.ThemeIcon.WindowClose), self.tr('Close') )
        self.buttonCancel.clicked.connect(self._on_cancel_clicked)
        self.layoutFormActionButtons.addWidget(self.buttonCancel, alignment=Qt.AlignmentFlag.AlignRight)

        # generic horizontal lines
        horzline = QFrame()
        horzline.setFrameShape(QFrame.Shape.HLine)
        horzline.setFrameShadow(QFrame.Shadow.Sunken)

        self.layoutForm.addLayout(self.layoutFormHdr)
        self.layoutForm.addLayout(self.layoutFormSQLDescription)
        self.layoutForm.addLayout(self.layoutFormMain)
        self.layoutForm.addWidget(horzline)
        self.layoutForm.addLayout(self.layoutFormActionButtons)

        colfctr = 90
        self.setMinimumWidth(colfctr*len(colNames))

    @Slot()
    def DLResults(self):
        ExcelFileNamePrefix = "SQLresults"
        # Create a dictionary of records from the model
        row_count = self._qmodel.rowCount()
        col_count = self._qmodel.columnCount()
        column_names = [self._qmodel.headerData(i, Qt.Orientation.Horizontal) for i in range(col_count)]

        Excel_qdict = []
        for row in range(row_count):
            record = {}
            for col in range(col_count):
                value = self._qmodel.data(self._qmodel.index(row, col))
                record[column_names[col]] = value
            Excel_qdict.append(record)

        # Create an Excel workbook and save it
        xlws = cExcelFile()
        dfltws = xlws.active
        xlws.load_from_listofdict(Excel_qdict, 'SQLResults')
        if dfltws is not None:
            xlws.remove(dfltws)
        filName, _ = QFileDialog.getSaveFileName(self,
            caption="Enter Spreadsheet File Name",
            filter="Excel (*.xlsx);;All files (*.*)",
            selectedFilter="Excel (*.xlsx)",
        )
        if filName and isinstance(xlws, Workbook):
            xlws.save(filName)

    def _return_to_sql(self):
        self.ReturnToSQL.emit()

    def _on_cancel_clicked(self):
        # Emit the cancel signal.
        self.closeBoth.emit()

    def closeEvent(self, event):
        self.closeMe.emit()  # Emit the signal
        event.accept()  # Accept the close event (allows the window to close)
# QWShowSQL
    def end_of_class(self):
        """ place this after the all methods and comments in the class, to avoid accidentally leaving out a method or comment when copying/pasting or refactoring code"""
        pass


class cMRunSQL(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)

        from calvincTools import calvincTools
        app_sessionmaker = calvincTools().app_sessionmaker
        assert app_sessionmaker is not None, "app_sessionmaker must be provided"
        self.app_sessionmaker = app_sessionmaker

        self.inputSQL:str|None = None
        self.qmodel:SQLAlchemySQLQueryModel
        self.colNames:str|List[str]|None = None
        self.wndwAlive:Dict[str,bool] = {}

        self.wndwGetSQL = QWGetSQL(parent)
        self.wndwGetSQL.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.wndwGetSQL.runSQL.connect(self.rawSQLexec)
        self.wndwGetSQL.cancel.connect(self._on_cancel)
        self.wndwAlive['Get'] = True
        self.wndwGetSQL.destroyed.connect(lambda: self.wndwDest('Get'))

        self.wndwShowSQL: QWShowSQL     # will be redefined later

    def wndwDest(self, whichone:str):
        self.wndwAlive[whichone] = False

    def show(self):
        self.wndwGetSQL.show()

    @Slot(str)  #type: ignore
    def rawSQLexec(self, inputSQL:str):
        #TODO: choose session - put in user control
        engine = self.app_sessionmaker().get_bind()

        self.qmodel = SQLAlchemySQLQueryModel(inputSQL, engine)

        self.rawSQLshow()

    def rawSQLshow(self):
        self.wndwShowSQL = QWShowSQL(self.qmodel, self.parent())
        self.wndwShowSQL.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.wndwShowSQL.ReturnToSQL.connect(self._ShowToGetSQL)
        self.wndwShowSQL.closeBoth.connect(self._on_cancel)

        self.wndwAlive['Show'] = True
        self.wndwShowSQL.destroyed.connect(lambda: self.wndwDest('Show'))


        self.wndwGetSQL.hide()
        self.wndwShowSQL.show()

    @Slot()
    def _ShowToGetSQL(self):
        if self.wndwAlive.get('Show'):
            self.wndwShowSQL.close()
        self.wndwGetSQL.show()

    @Slot()
    def _on_cancel(self):
        # Handle the cancellation by closing both windows.
        self._close_all()

    def _close_all(self):
        # Close the child widget if it exists.
        if self.wndwAlive.get('Get'):
            self.wndwGetSQL.close()
        if self.wndwAlive.get('Show'):
            self.wndwShowSQL.close()
        # Close this widget (cMRunSQL) as well.
        self.close()
# cMRunSQL
    def end_of_class(self):
        """ place this after the all methods and comments in the class, to avoid accidentally leaving out a method or comment when copying/pasting or refactoring code"""
        pass