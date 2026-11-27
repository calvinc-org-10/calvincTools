from typing import (Dict, List, Any, Type, Callable, cast, )
from dataclasses import dataclass
# from warnings import deprecated  # python >= 3.13

from PySide6.QtCore import (
    QAbstractTableModel, 
    )

from openpyxl import (Workbook, load_workbook, )
from openpyxl.styles import PatternFill, Font, fills, colors
from openpyxl.utils import get_column_letter
from openpyxl.utils.datetime import from_excel, WINDOWS_EPOCH

from .cQModels import (SQLAlchemyTableModel, )
from ..database import Repository

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


ExcelWorkbook_fileext = ".XLSX"
HEADER_FREEZE_PANE_CELL = 'A2'
HEADER_FONT = Font(bold=True)
HEADER_FILL = PatternFill(
    fill_type=fills.FILL_SOLID,
    start_color=colors.Color("00808080"),
    end_color=colors.Color("00808080")
)

class SprdsheetFldDescriptor:
    """Descriptor for spreadsheet fields, defining validation rules and cleaning procedures."""
    """Create a field descriptor for spreadsheet field validation.
    
    Args:
        ModelFldName (str): The name of the field in the TargetModel.
        AllowedTypes: tuple (or singleton) specifying allowed types
            for the field value. If not provided, defaults to str.
        CleanProc: Optional cleaning procedure to apply to the field value.
    
    Returns:
        dict: Field descriptor dictionary with ModelFldName and AllowedTypes.
    """
    ModelFldName:str
    CalculatedFld:bool
    AllowedTypes:tuple
    CleanProc:Any

    def __init__(self, ModelFldName:str, CalculatedFld=None, AllowedTypes=None, CleanProc=None) -> None:
        self.ModelFldName:str = ModelFldName
        self.CalculatedFld:bool = CalculatedFld or False
        self.AllowedTypes:tuple = AllowedTypes if AllowedTypes is not None else (str, )
        self.CleanProc = CleanProc

@dataclass
class svfromws_errorRecord:
    error_type: str  # 'worksheet', 'missing_columns', 'validation', 'type_error'
    error_message: str
    row_number: int | None = None
    incoming_row: dict | None = None
    processed_row: dict | None = None

class cExcelFile(Workbook):
    """Subclass of openpyxl's Workbook to add custom functionality for Excel file handling."""
    
    # this is only used in save_to_listdict. Should these be local to that method instead of class attributes?
    num_rows = None
    nRows = None
    nRowsSkipped = None
    
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # Additional initialization can be added here if needed
    

    @staticmethod
    def _calculate_freeze_address(num_cols: int) -> str:
        """Convert column count to Excel freeze panes cell address.
        
        Args:
            num_cols: Number of columns to freeze (0 = freeze only header row)
            
        Returns:
            Excel cell address for freeze_panes (e.g., 'A2', 'B2', 'D2')
            
        Examples:
            _calculate_freeze_address(0) → 'A2'   # Only header row frozen
            _calculate_freeze_address(1) → 'B2'   # Cols A + header
            _calculate_freeze_address(3) → 'D2'   # Cols A-C + header
        """
        
        if num_cols <= 0:
            return 'A2'  # Default: freeze only header row
        
        freeze_col_letter = get_column_letter(num_cols + 1)
        return f'{freeze_col_letter}2'
    # _calculate_freeze_address

    def auto_adjust_columns(self, ws, max_width: int = 50) -> None:
        """Auto-fit column widths based on content.
        
        Args:
            ws: Worksheet to adjust
            max_width: Maximum column width (prevents extremely wide columns)
        """
        from openpyxl.worksheet.worksheet import Worksheet
        
        if not isinstance(ws, Worksheet):
            logger.warning("auto_adjust_columns: ws is not a valid Worksheet")
            return
        
        for col_index, column in enumerate(ws.columns, start=1):
            max_length = 0
            column_letter = get_column_letter(col_index)
            
            for cell in column:
                try:
                    if cell.value:
                        cell_length = len(str(cell.value))
                        max_length = max(max_length, cell_length)
                except Exception as e:
                    logger.debug(f"Error measuring cell {cell.coordinate}: {e}")
                    pass
            
            # Set width: content length + 2 for padding, capped at max_width
            adjusted_width = min(max_length + 2, max_width)
            ws.column_dimensions[column_letter].width = adjusted_width
            
        logger.debug(f"Auto-adjusted column widths in worksheet '{ws.title}'")
    # auto_adjust_columns

    def load_from_listofdict(self,
        qlist:List[Dict[str, Any]], 
        wsName:str|None = None,
        freezecols:int = 0, 
        auto_adjust: bool = True,
        ) -> bool:
        """
        Load data from a SQLAlchemy model into the workbook.
        
        Args:
        qset: a QAbstractTableModel or list of dictionaries
        flName: the name of the file to be built (WITHOUT extension!).  It's stored on the server.  If it's to be dl'd, the caller does that
        freezecols = 0: the number of columns to freeze to the left
        auto_adjust: Auto-fit column widths after loading (default: True)

        The top row contains the field names, is always frozen, is bold and is shaded grey

        Returns True if the workbook was successfully populated from the qset, False otherwise.
        """
        
        # create empty worksheet
        wb = self
        baseName = wsName or "Sheet"
        use_parens = not wsName
        candidate = baseName
        n = 0
        while candidate in wb.sheetnames:
            n += 1
            candidate = f"{baseName}({n})" if use_parens else f"{baseName}{n}"
        ws = wb.create_sheet(title=candidate)

        # header row is names of columns
        if qlist:
            fields = list(qlist[0])
            ws.append(fields)

            # append each row
            for row in qlist:
                ws.append(list(row.values())) # type: ignore

            # make header row bold, shade it grey, freeze it
            # ws.show_gridlines = True  #Nope - this is a R/O attribute
            for cell in ws[1]: # type: ignore
                cell.font = HEADER_FONT
                cell.fill = HEADER_FILL
                
            # convert row1 and cols:freezecols to an address (A=0, B=1, C=2 etc) for line below
            freeze_address = self._calculate_freeze_address(freezecols)
            ws.freeze_panes = freeze_address
            logger.debug(f"Set freeze panes to {freeze_address} for {freezecols} columns")

            # Auto-adjust column widths if requested
            if auto_adjust:
                self.auto_adjust_columns(ws)
    
        #endif qlist

        return True
    # load_from_listofdict
    
    def load_from_SQLAlchModel(self,
        qset:SQLAlchemyTableModel, 
        wsName:str|None = None,
        freezecols:int = 0, 
        ) -> bool:
        """
        qset: a QAbstractTableModel or list of dictionaries
        flName: the name of the file to be built (WITHOUT extension!).  It's stored on the server.  If it's to be dl'd, the caller does that
        freezecols = 0: the number of columns to freeze to the left
        The top row contains the field names, is always frozen, is bold and is shaded grey

        Returns True if the workbook was successfully populated from the qset, False otherwise.
        """

        # far easier to process a list of dictionaries, so...
        if isinstance(qset,QAbstractTableModel):
            # make this a util
            qlist = qset.getDataAsList()
        elif isinstance(qset,list):
            qlist = qset
        else:
            return False
        if qlist:
            if not isinstance(qlist[0],dict):
                # review this later ...
                try:
                    qlist = [n.__dict__ for n in qlist]
                except:
                    qlist = []

        return self.load_from_listofdict(qlist, wsName, freezecols)
    # load_from_SQLAlchModel

    @classmethod
    def load_from_file(cls, filename: str, *args, **kwargs) -> "cExcelFile | None":
        """Load an existing Excel file and return it as cExcelFile.

        Args:
            filename (str): The name of the file to load, including extension.
            For other arguments, see openpyxl.reader.excel.load_workbook() documentation.

        Returns:
            Loaded cExcelFile instance, or None on failure.
        """
        try:
            wb = load_workbook(filename, *args, **kwargs)
            wb.__class__ = cls
            return cast("cExcelFile", wb)
        except Exception as e:
            logger.error(f"Error loading file {filename}: {e}")
            return None
    # load_from_file

    def validate_worksheet(self,
        WksheetName: str | None = None,
        SprdsheetFlds: Dict[str, SprdsheetFldDescriptor] | None = None,
        required_columns: List[str] | None = None
    ) -> tuple[bool, List[str]]:
        """Validate worksheet structure before processing.
        
        Args:
            WksheetName: Worksheet name (None = active sheet)
            SprdsheetFlds: Field descriptor dict
            required_columns: List of required model field names (mapped via SprdsheetFlds)
            
        Returns:
            (is_valid, error_messages) - tuple with validation result and error list
            
        Checks:
            1. Worksheet exists
            2. Has header row
            3. Expected columns present
            4. Required columns present
            5. No duplicate columns
            6. At least one data row present

        # **Usage:**
        # wb = cExcelFile.load_from_file('import.xlsx')

        # is_valid, errors = wb.validate_worksheet(
        #     WksheetName='Users',
        #     SprdsheetFlds=field_defs,
        #     required_columns=['name', 'email']
        # )

        # if not is_valid:
        #     print("Validation failed:")
        #     for error in errors:
        #         print(f"  - {error}")
        # else:
        #     print("Worksheet validation passed! Safe to import.")
        #     # Now proceed with import
        #     data = wb.save_to_listofdict(...)
        """
        errors = []
        wb = self
        
        # Check 1: Worksheet exists
        ws = wb[WksheetName] if WksheetName in wb.sheetnames else wb.active
        if ws is None:
            errors.append(f"Worksheet '{WksheetName}' not found in workbook")
            return (False, errors)
        
        # Check 2: Has header row
        if ws.max_row < 1:
            errors.append("Worksheet is empty (no header row)")
            return (False, errors)
        
        # Check 3: Check for expected columns
        if SprdsheetFlds:
            header_row = ws[1]
            header_values = [cell.value for cell in header_row if cell.value]
            
            # Check 4: Required columns present
            if required_columns:
                required_spsheet_cols = set()
                for req_col in required_columns:
                    # Find spreadsheet column name that maps to this model field
                    for spsheet_col, desc in SprdsheetFlds.items():
                        if desc.ModelFldName == req_col:
                            required_spsheet_cols.add(spsheet_col)
                            break
                
                missing = required_spsheet_cols - set(header_values)
                if missing:
                    errors.append(f"Missing required columns: {', '.join(missing)}")
            
            # Check 5: No duplicate columns
            seen = {}
            for col_idx, cell in enumerate(header_row, 1):
                if cell.value in SprdsheetFlds and cell.value in seen:
                    errors.append(f"Duplicate column '{cell.value}' at columns "
                                f"{seen[cell.value]} and {col_idx}")
                if cell.value in SprdsheetFlds:
                    seen[cell.value] = col_idx
        
        # Check 6: At least one data row
        if ws.max_row < 2:
            errors.append("Worksheet has no data rows (only header)")
        
        is_valid = len(errors) == 0
        return (is_valid, errors)
    # validate_worksheet
    
# move this into a method of cExcelFile
# class UpldSprdsheet():
    """Base class for handling spreadsheet uploads with field validation.
    
    This class provides functionality for processing uploaded spreadsheets,
    validating field types, and cleaning data according to defined rules.
    
    Attributes:
        TargetModel: The target ORM model class for the spreadsheet data.
        SprdsheetDateEpoch: Date epoch used for spreadsheet date conversion.
        SprdsheetFlds (dict): Dictionary mapping spreadsheet field names to field descriptors.
    
    This is now implemented in save_to_SQLAlchemyModel method of cExcelFile, which uses the SprdsheetFlds dict 
    TODO: create save_to_listofdict method 
    
    """
    # shoudl I just go on and make this a dataclass?
      # key will be the SprdsheetName, value is a SprdsheetFldDescriptor
    SprdsheetFlds:Dict[str,SprdsheetFldDescriptor] = {}  # key will be the SprdsheetName, value is a SprdsheetFldDescriptor
      # key will be the SprdsheetName, value is a SprdsheetFldDescriptor

    @staticmethod
    def _normalize_cleanproc_result(result: Any) -> tuple[bool, Any]:
        """Normalize CleanProc return value to consistent (usefld, cleanval) tuple.
        
        CleanProc can return:
        - tuple[bool, Any]: (use_field, cleaned_value) - preferred format
        - Any other value: treated as cleaned_value, usefld=True if not None
        
        This method normalizes both formats to standard tuple.
        
        Args:
            result: Return value from CleanProc callable
            
        Returns:
            tuple[bool, Any]: (usefld, cleanval) where
                usefld=True means include field in output
                cleanval is the processed value
                
        Examples:
            _normalize_cleanproc_result((True, 'value'))
                → (True, 'value')
            
            _normalize_cleanproc_result((False, None))
                → (False, None)
            
            _normalize_cleanproc_result('value')
                → (True, 'value')
            
            _normalize_cleanproc_result(None)
                → (False, None)
        """
        if isinstance(result, tuple) and len(result) == 2:
            # Already in correct format
            return result
        
        # Convert non-tuple to standard format
        use_field = result is not None
        clean_value = result if use_field else None
        return (use_field, clean_value)
    # _normalize_cleanproc_result
    def cleanupfld(self, 
            spshtFldNm: str, 
            dbFldNm: str, 
            val: Any, 
            rowdict: Dict[str, Any]
        ) -> tuple[bool, Any]:
        """Clean and validate a field value according to its allowed types.
        
        Args:
            fld: Field name to clean.
            val: Value to clean and validate.
            row: The entire row of data, which may be used in the cleaning procedure.
        
        Returns:
            tuple: (usefld, cleanval) where usefld is True if the field should be used,
                and cleanval is the cleaned value.
        """
        usefld = False
        cleanval = val
        
        if spshtFldNm not in self.SprdsheetFlds:
            # just feed the value back
            usefld = True
            cleanval = val
            return usefld, cleanval
        # endif fld not in self.SprdsheetFlds
        
        cleanDesc = self.SprdsheetFlds[spshtFldNm]
        if callable(cleanDesc.CleanProc):
            result = cleanDesc.CleanProc(spshtFldNm, dbFldNm, val, rowdict)
            usefld, cleanval = self._normalize_cleanproc_result(result)
            if not usefld:
                return usefld, cleanval
        # if callable(cleanDesc.CleanProc)

        # Validate the cleaned value against the allowed types for this field.
        allowed_types = cleanDesc.AllowedTypes
        if not isinstance(allowed_types, tuple) or allowed_types == ():
            allowed_types = (str, )
        usefld = isinstance(cleanval, allowed_types)
        
        return usefld, cleanval
    # cleanupfld

    def save_to_SQLAlchemyModel(self, 
        ssnmaker, 
        TargetModel:Type[Any],
        WksheetName, # default to None?
        SprdsheetFlds:Dict[str,SprdsheetFldDescriptor]|None = None, 
        required_columns: List[str]|None = None,      # these are model field names, not spreadsheet column names - they are mapped to spreadsheet column names via SprdsheetFlds
        progress_interval: int = 100,
        progress_callback:Callable[[int, int], None]|None = None,
        validation_callback: Callable[[Dict[str, Any]], None]|None = None,
        batch_size: int = 1000,
        dry_run: bool = False,
        ) -> List[svfromws_errorRecord]:
        """Process the imported spreadsheet data and save it to the database.
        
        Args:
            ssnmaker: Database session for saving the processed data.
            TargetModel: The SQLAlchemy model class to which the data will be saved.
            WksheetName: Name of the worksheet being processed.
            SprdsheetFlds: Mapping of spreadsheet field names to their descriptors.
            required_columns: List of required model field names.
            progress_interval: Interval at which progress updates are reported.
            progress_callback: Callback function for reporting progress.
            validation_callback: Callback function for validating each record.
            batch_size: Number of records to process in each batch.
            dry_run: If True, no changes will be committed to the database.
            
        Returns:
            List of error records (records with $error keys)
        """

        dbdata_list, err_list = self.save_to_listofdict(
            WksheetName, 
            SprdsheetFlds, 
            required_columns, 
            progress_interval, 
            progress_callback, 
            validation_callback
        )
        # err_list = [d for d in record_data if any(str(k).startswith("$error") for k in d)]
        # dbdata_list = [d for d in record_data if not any(str(k).startswith("$error") for k in d)]
        
        if len(dbdata_list) > 0:
            if dry_run:
                logger.info(f"DRY RUN: Would insert {len(dbdata_list)} records in "
                        f"{(len(dbdata_list) + batch_size - 1) // batch_size} batches")
            else:
                # Insert in batches
                batch_count = 0
                for i in range(0, len(dbdata_list), batch_size):
                    batch = dbdata_list[i:i + batch_size]
                    batch_count += 1
                    
                    try:
                        Repository(ssnmaker, TargetModel).bulk_add_from_listofdict(batch)
                        logger.info(f"Inserted batch {batch_count} ({len(batch)} records)")
                    except Exception as e:
                        logger.error(f"Error inserting batch {batch_count}: {e}", exc_info=True)
                        err = svfromws_errorRecord(
                            error_type='insertion',
                            error_message=f"Error inserting batch {batch_count}: {e}",
                            row_number=batch_count
                        )
                        err_list.append(err)
                        # raise
                    # end try bulk add
                # end for each batch
            # end if dry_run
        # end if there are records to insert
        
        return err_list
    # save_to_SQLAlchemyModel
    

    def save_to_listofdict(self, 
        WksheetName, # default to None?
        SprdsheetFlds:Dict[str,SprdsheetFldDescriptor]|None = None, 
        required_columns: List[str]|None = None,      # these are model field names, not spreadsheet column names - they are mapped to spreadsheet column names via SprdsheetFlds
        progress_interval: int = 100,
        progress_callback: Callable[[int, int], None]|None = None,
        validation_callback: Callable[[Dict[str, Any]], None]|None = None,
        ) -> tuple[List[Dict[str, Any]], List[svfromws_errorRecord]]:
      # key will be the SprdsheetName, value is a SprdsheetFldDescriptor
        """Process the imported spreadsheet data and save it to the database.
        
        Args:
            dbsession: Database session for saving the processed data.
            SprsheetName: Name of the spreadsheet being processed.
            data: The data extracted from the spreadsheet to be processed.
            
        """
        wb = self
        err_list:List[svfromws_errorRecord] = []
        data_list = []
                
        if SprdsheetFlds is not None:
            self.SprdsheetFlds = SprdsheetFlds
        
        ws = wb[WksheetName] if WksheetName in wb.sheetnames else wb.active
        if ws is None:
            logger.error(f"Worksheet {WksheetName} not found in workbook.")
            err = svfromws_errorRecord(
                error_type='worksheet',
                error_message=f"Worksheet {WksheetName} not found in workbook."
            )
            err_list.append(err)
            return data_list, err_list
                
        SprshtHdrRow = ws[1]
        required_columns = required_columns if required_columns is not None else []
        dbFld_to_sprshtCol:dict[str, Any] = {req_col: None for req_col in required_columns}
        for col in SprshtHdrRow:
            if col.value in self.SprdsheetFlds:
                colval = str(col.value)
                modlFldNm = self.SprdsheetFlds[colval].ModelFldName
                colIndx = (col.column or 0) - 1
                # has this field already been mapped?
                if modlFldNm in dbFld_to_sprshtCol and dbFld_to_sprshtCol[modlFldNm] is not None:
                    # yes, that's not good - duplicate column in spreadsheet.  Warn and skip this column
                    logger.warning(f"Warning: Duplicate column '{colval}' in spreadsheet. Column {dbFld_to_sprshtCol[modlFldNm]+1} Already mapped to model field '{modlFldNm}'. Skipping this column ({colIndx+1}).")
                    continue
                dbFld_to_sprshtCol[modlFldNm] = colIndx
        # end for col in SprshtHdrRow
        
        if any(val is None for val in dbFld_to_sprshtCol.values()):
            missing_cols = [col for col, val in dbFld_to_sprshtCol.items() if val is None]
            logger.error(f"Error: Missing required columns in spreadsheet: {', '.join(missing_cols)}")
            err = svfromws_errorRecord(
                error_type='worksheet',
                error_message=f"Missing required columns in spreadsheet: {', '.join(missing_cols)}"
            )
            err_list.append(err)
            return data_list, err_list
        # end if any missing required columns
        
        # Process each row in the worksheet
        self.num_rows = ws.max_row
        self.nRows = 0
        self.nRowsSkipped = 0
        for row in ws.iter_rows(min_row=2, values_only=True):
            self.nRows += 1
            if self.nRows % progress_interval == 0:
                print(f"Processing row {self.nRows} of {self.num_rows}...")
                if callable(progress_callback):
                    progress_callback(self.nRows, self.num_rows)
            # if nRows % progress_interval == 0
            
            # convert row to dict for easier processing - keys are model field names, values are cell values
            rowdict =  {modlFldNm: row[colIndx] for modlFldNm, colIndx in dbFld_to_sprshtCol.items() if colIndx is not None and colIndx < len(row)}
            
            # does this row have all required columns?
            if any([rowdict.get(req_col, None) in (None, '') for req_col in required_columns]):
                self.nRowsSkipped += 1
                continue
            
            record_data = {}
            # process the row
            for dbFldNm, val in rowdict.items():
                spshtFldNm = next((fld for fld, desc in self.SprdsheetFlds.items() if desc.ModelFldName == dbFldNm), None)
                if spshtFldNm:
                    usefld, cleanval = self.cleanupfld(spshtFldNm, dbFldNm, val, rowdict)
                    if usefld:
                        record_data[dbFldNm] = cleanval
            # end for dbFld, colIndx in dbFld_to_SsprshtCol.items()
            # process calculated fields, if any
            for spshtFldNm, desc in self.SprdsheetFlds.items():
                if not desc.CalculatedFld:
                    continue
                dbFldNm = desc.ModelFldName
                usefld, cleanval = self.cleanupfld(spshtFldNm, dbFldNm, None, rowdict)
                if usefld:
                    record_data[dbFldNm] = cleanval
            # end for fld_name, desc in self.SprdsheetFlds.items()
            
            validRecord = True            
            if callable(validation_callback):
                validRecord = validation_callback(record_data)

            # create an instance of TargetModel with record_data and add it to the session
            if validRecord:
                data_list.append(record_data)
            else:
                self.nRowsSkipped += 1
                print(f"Row {self.nRows} skipped due to validation failure.\n    {record_data}")
                err = svfromws_errorRecord(
                    error_type='validation',
                    error_message=f"Row {self.nRows} skipped due to validation failure.",
                    row_number=self.nRows,
                    incoming_row=rowdict,
                    processed_row=record_data,
                )
                err_list.append(err)
            # endif validRecord
        # for each row
        
        return data_list, err_list
    # save_to_SQLAlchemyModel

# cExcelFile
    def end_of_class(self):
        """Placeholder method to indicate the end of the cExcelFile class definition."""
        pass
