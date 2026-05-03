from calvincTools.utils import SQLAlchemySQLQueryModel, pleaseWriteMe
from calvincTools.utils.forms.widgets import cQFmNameLabel


from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QFormLayout, QHBoxLayout, QHeaderView, QLabel, QTableView, QVBoxLayout, QWidget
from sqlalchemy import Engine


from typing import List


class OpenTable(QWidget):

    class cOpnTblDlgGetTable(QDialog):
        _tableListSQL:str = 'PRAGMA table_list;'

        def __init__(self, parent:QWidget|None = None):
            super().__init__(parent)

            from calvincTools import calvincTools
            app_sessionmaker = calvincTools().app_sessionmaker

            self.setWindowModality(Qt.WindowModality.WindowModal)
            self.setWindowTitle(parent.windowTitle() if parent else 'Choose Table')

            layoutTableName = QHBoxLayout()
            lblTableName = QLabel(self.tr('Table to Show'))
            self.combobxTableName = QComboBox(self)
            self.combobxTableName.addItems(self.TableList(app_sessionmaker))
            layoutTableName.addWidget(lblTableName)
            layoutTableName.addWidget(self.combobxTableName)

            dlgButtons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel,
                Qt.Orientation.Horizontal,
                )
            dlgButtons.accepted.connect(self.accept)
            dlgButtons.rejected.connect(self.reject)

            layoutMine = QVBoxLayout()
            layoutMine.addLayout(layoutTableName)
            layoutMine.addWidget(dlgButtons)

            self.setLayout(layoutMine)

        def TableList(self, app_sessionmaker) -> List:

            db:Engine = app_sessionmaker().get_bind()

            qmodel = SQLAlchemySQLQueryModel(self._tableListSQL, db)

            colIdx = qmodel.colIndex('name')
            if colIdx < 0:
                # no 'name' column found
                # raise ValueError("No 'name' column found in the table list query result.")
                return []

            # retList = [qmodel.record(n)[colIdx] for n in range(qmodel.rowCount())]
            retList = [qmodel.data(qmodel.index(n, colIdx)) for n in range(qmodel.rowCount())]
            return retList

        def exec_DlgGetTbl(self):
            ret = super().exec()
            # later - prevent lvng if lnedtGroupName blank
            return (
                ret,
                self.combobxTableName.currentText()    if ret==self.DialogCode.Accepted else None,
                )

    def __init__(self, tbl:str|None = None, parent:QWidget|None = None):
        super().__init__(parent)

        # font = QFont()
        # font.setPointSize(12)
        # self.setFont(font)

        from calvincTools import calvincTools
        app_sessionmaker = calvincTools().app_sessionmaker
        assert app_sessionmaker is not None, "app_sessionmaker must be provided"
        db:Engine=app_sessionmaker().get_bind()

        if not tbl:
            # get tbl name
                # use self._tableListSQL
            # read all table names
            # present and select
            tbl = self.chooseTable()

        # for testing ...
        # tbl = 'incShip_hbl'

        # read into model
        # verify tbl exists
        # error, rows, colNames = (None, [], [])
        # error, rows, colNames = self.getTable(tbl)
        # if error:
        #     raise error

        # tblWidget = self.tableWidget(rows, colNames)
        tblWidget = self.tableWidget(tbl, db)
        self.model = tblWidget.model()
        # bring all rows in so rowCount will be correct
        # while tblWidget.model().canFetchMore():
        #     tblWidget.model().fetchMore()
        rows = tblWidget.model().rowCount()
        colNames = [tblWidget.model().headerData(n, Qt.Orientation.Horizontal) for n in range(tblWidget.model().columnCount())]
        # present TableView

        # save incoming for future use if needed
        self.rows = rows
        self.colNames = colNames

        self.layoutForm = QVBoxLayout(self)

        #TODO: make Title the name of the table        
        #TODO: note on screen that this form is RO        
        # Form Header Layout
        self.layoutFormHdr = QVBoxLayout()
        self.lblFormName = cQFmNameLabel()
        self.lblFormName.setText(self.tr('Table'))
        self.setWindowTitle(self.tr('Table'))
        self.layoutFormHdr.addWidget(self.lblFormName)

        self.layoutFormTableDescription = QFormLayout()
        lblnRecs = QLabel()
        lblnRecs.setText(f'{rows}')
        lblcolNames = QLabel()
        lblcolNames.setText(str(colNames))
        self.layoutFormTableDescription.addRow('rows:', lblnRecs)
        self.layoutFormTableDescription.addRow('cols:', lblcolNames)

        # main area for displaying SQL
        self.layoutFormMain = QVBoxLayout()
        self.layoutFormMain.addWidget(tblWidget)

        # nope - this is RO
        # # Add a add row button
        # addrow_button = QPushButton("Add Row")
        # addrow_button.clicked.connect(lambda: self.addRow())

        # # Add a save button
        # save_button = QPushButton("Save Changes")
        # save_button.clicked.connect(lambda: self.model.save_changes() or print("Saved!"))    # type: ignore

        # layoutButtons = QHBoxLayout()
        # layoutButtons.addWidget(addrow_button)
        # layoutButtons.addWidget(save_button)

        self.layoutForm.addLayout(self.layoutFormHdr)
        self.layoutForm.addLayout(self.layoutFormTableDescription)
        self.layoutForm.addLayout(self.layoutFormMain)
        # self.layoutForm.addLayout(layoutButtons)

    def chooseTable(self) -> str|None:
        dlg = self.cOpnTblDlgGetTable(self)
        retval, tblName = dlg.exec_DlgGetTbl()
        return tblName if retval == QDialog.DialogCode.Accepted else None


    def getTable(self, tblName:str): # -> Tuple[Exception|None, List[Dict[str, Any]], List[str]|str]:
        pleaseWriteMe('fix getTable in class OpenTable', parent=self)
        # inputSQL:str = f'SELECT * FROM {tblName}'
        # # inputSQL:str = f'SELECT * FROM %(tblName)s'
        # sqlerr = None
        # with db.connection.cursor() as djngocursor:
        #     try:
        #         djngocursor.execute(inputSQL)
        #         # djngocursor.execute(inputSQL, [tblName])
        #     except Exception as err:
        #         sqlerr = err
        #     colNames = []
        #     rows = []
        #     if not sqlerr:
        #         if djngocursor.description:
        #             colNames = [col[0] for col in djngocursor.description]
        #             rows = dictfetchall(djngocursor)
        #         else:
        #             colNames = 'NO RECORDS RETURNED; ' + str(djngocursor.rowcount) + ' records affected'
        #             rows = []
        #         #endif cursor.description
        #     else:  
        #         # nothing to do
        #         ...
        #     #endif not sqlerr
        # #end with

        # return (sqlerr, rows, colNames)

    # def tableWidget(self, rows:List[Dict[str, Any]], colNames:str|List[str]) -> QTableView:
    def tableWidget(self, tbl:str|None, db:Engine) -> QTableView:
        sqlstat = f"SELECT * FROM {tbl}" if tbl else "SELECT * FROM sqlite_master WHERE type='table';"
        resultModel = SQLAlchemySQLQueryModel(sqlstat, db, self.parent())
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
        resultTable.setModel(resultModel)

        return resultTable

    def addRow(self):
        self.model.insertRow(self.model.rowCount())

    def end_of_class(self):
        """ place this after the all methods and comments in the class, to avoid accidentally leaving out a method or comment when copying/pasting or refactoring code"""
        pass