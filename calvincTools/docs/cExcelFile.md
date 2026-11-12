# cExcelFile API Documentation

## Overview

`cExcelFile` is a subclass of `openpyxl.Workbook` that extends Excel file handling capabilities with custom functionality for loading data from various sources (lists of dictionaries, SQLAlchemy models) and processing spreadsheet data for database operations.

**Module:** `calvincTools.utils.Excel`  
**Base Class:** `openpyxl.Workbook`  
**File:** `calvincTools/utils/Excel.py`

---

## Class Definition

```python
class cExcelFile(Workbook):
    """Subclass of openpyxl's Workbook to add custom functionality for Excel file handling."""
```

---

## Attributes

### Instance Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `num_rows` | `int \| None` | Total number of rows in the active worksheet |
| `nRows` | `int \| None` | Counter for rows processed during import operations |
| `nRowsSkipped` | `int \| None` | Counter for rows skipped during import operations |
| `SprdsheetFlds` | `Dict[str, SprdsheetFldDescriptor]` | Dictionary mapping spreadsheet column names to field descriptors for validation and cleaning |

### Module-Level Constants

| Constant | Type | Value | Description |
|----------|------|-------|-------------|
| `ExcelWorkbook_fileext` | `str` | `".XLSX"` | Default Excel file extension |

---

## Inner Classes

### SprdsheetFldDescriptor

Descriptor class for spreadsheet fields, defining validation rules and data cleaning procedures.

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `ModelFldName` | `str` | Name of the corresponding field in the target ORM model |
| `CalculatedFld` | `bool` | Whether this field is calculated (not sourced from spreadsheet) |
| `AllowedTypes` | `tuple` | Tuple of allowed Python types for field values. Defaults to `(str,)` |
| `CleanProc` | `Callable \| None` | Optional cleaning/validation function to apply to field values |

#### Constructor

```python
def __init__(self, 
             ModelFldName: str, 
             CalculatedFld=None, 
             AllowedTypes=None, 
             CleanProc=None):
```

**Parameters:**
- `ModelFldName` (str): Name of the field in the target database model
- `CalculatedFld` (bool, optional): Mark field as calculated; defaults to False
- `AllowedTypes` (tuple, optional): Tuple of allowed types (e.g., `(str, int, float)`); defaults to `(str,)`
- `CleanProc` (callable, optional): Function for custom cleaning/validation

**Example:**

```python
SprdsheetFldDescriptor(
    ModelFldName='user_name',
    AllowedTypes=(str,),
    CleanProc=lambda fld, dbfld, val, row: (True, val.strip() if val else None)
)
```

---

## Methods

### `__init__(*args, **kwargs)`

Initialize a cExcelFile instance.

**Parameters:**
- `*args`: Positional arguments passed to parent `Workbook` class
- `**kwargs`: Keyword arguments passed to parent `Workbook` class

**Returns:** None

**Example:**

```python
wb = cExcelFile()
```

---

### `load_from_listofdict(qlist, wsName=None, freezecols=0)`

Load data from a list of dictionaries into the workbook.

**Parameters:**
- `qlist` (List[Dict[str, Any]]): List of dictionaries where each dictionary represents a row
- `wsName` (str, optional): Name for the new worksheet; auto-generates if not provided
- `freezecols` (int, optional): Number of columns to freeze from the left (default: 0)
  - **Note:** Currently only freezes the header row; column freezing is not yet implemented (see TODO)

**Returns:** `bool` - True if data was successfully loaded, False otherwise

**Behavior:**
- Creates a new worksheet with auto-generated name if `wsName` conflicts with existing sheets
- First row contains field names (column headers), formatted as bold text on grey background
- Header row is always frozen (first row remains visible when scrolling)
- Each subsequent row contains the values from corresponding dictionary

**Example:**

```python
data = [
    {'name': 'Alice', 'age': 30, 'city': 'NYC'},
    {'name': 'Bob', 'age': 25, 'city': 'LA'},
]
wb = cExcelFile()
success = wb.load_from_listofdict(data, wsName='People')
if success:
    wb.save('people.xlsx')
```

---

### `load_from_SQLAlchModel(qset, wsName=None, freezecols=0)`

Load data from a SQLAlchemy model or QAbstractTableModel into the workbook.

**Parameters:**
- `qset` (SQLAlchemyTableModel | QAbstractTableModel | list): Data source
  - Can be a `SQLAlchemyTableModel` instance
  - Can be a `QAbstractTableModel` (converts via `getDataAsList()`)
  - Can be a list of dictionaries or model instances
- `wsName` (str, optional): Name for the new worksheet
- `freezecols` (int, optional): Number of columns to freeze from the left (default: 0)

**Returns:** `bool` - True if data was successfully loaded, False otherwise

**Behavior:**
- Automatically converts QAbstractTableModel to list of dictionaries via `getDataAsList()`
- Converts model instances to dictionaries via `__dict__` attribute
- Delegates to `load_from_listofdict()` for actual data loading
- Returns False if conversion fails

**Example:**

```python
from calvincTools.models import User

# Assuming qset is a SQLAlchemyTableModel or query result
wb = cExcelFile()
success = wb.load_from_SQLAlchModel(qset, wsName='Users')
```

---

### `@classmethod load_from_file(filename, *args, **kwargs)`

Load an existing Excel file and return it as a cExcelFile instance.

**Parameters:**
- `filename` (str): Path to the Excel file to load (including extension)
- `*args`: Additional positional arguments passed to `openpyxl.load_workbook()`
- `**kwargs`: Additional keyword arguments passed to `openpyxl.load_workbook()`
  - Common options: `data_only=True`, `keep_vba=True`, etc.

**Returns:** `cExcelFile | None` - Loaded workbook instance, or None if loading fails

**Example:**

```python
wb = cExcelFile.load_from_file('existing_file.xlsx')
if wb is not None:
    # Process the workbook
    ws = wb.active
    for row in ws.iter_rows(values_only=True):
        print(row)
```

---

### `cleanupfld(spshtFldNm, dbFldNm, val, rowdict)`

Clean and validate a field value according to its field descriptor rules.

**Parameters:**
- `spshtFldNm` (str): Spreadsheet column name (key in `SprdsheetFlds`)
- `dbFldNm` (str): Database/model field name
- `val` (Any): Raw value from the spreadsheet cell
- `rowdict` (dict): Complete row data (dict of model field names to values), used by cleaning procedures

**Returns:** `tuple[bool, Any]` - (usefld, cleanval)
  - `usefld` (bool): Whether the field should be included in output
  - `cleanval` (Any): The cleaned/validated value

**Behavior:**
- If field is not in `SprdsheetFlds`, returns value as-is with `usefld=True`
- If field has a `CleanProc`, calls it first; accepts tuple return `(usefld, cleanval)`
- Then validates type against `AllowedTypes`
- Returns `usefld=True` only if value passes all validations

**Example:**

```python
desc = SprdsheetFldDescriptor(
    ModelFldName='email',
    AllowedTypes=(str,),
    CleanProc=lambda fld, dbfld, val, row: (True, val.strip().lower() if val else None)
)
cexcel.SprdsheetFlds['email_addr'] = desc

usefld, cleanval = cexcel.cleanupfld('email_addr', 'email', '  USER@EXAMPLE.COM  ', {})
# Returns: (True, 'user@example.com')
```

---

### `save_to_listofdict(WksheetName, SprdsheetFlds=None, required_columns=None, progress_interval=100, progress_callback=None, validation_callback=None)`

Process spreadsheet data and convert it to a list of dictionaries suitable for database insertion.

**Parameters:**
- `WksheetName` (str): Name of the worksheet to process (or None to use active sheet)
- `SprdsheetFlds` (Dict[str, SprdsheetFldDescriptor], optional): Field descriptors; if provided, overrides instance `SprdsheetFlds`
- `required_columns` (list, optional): List of required model field names (mapped via `SprdsheetFlds`); rows missing any required column are skipped
- `progress_interval` (int, optional): Print progress every N rows (default: 100)
- `progress_callback` (callable, optional): Function called with `(current_row, total_rows)` at progress intervals
- `validation_callback` (callable, optional): Function called with `(record_data)` for each processed row; return True to include, False to skip

**Returns:** `List[Dict[str, Any]]` - List of processed records
  - Valid records: dictionaries with model field names as keys
  - Invalid records: dictionaries with `$error-row<N>` key containing error message, plus `'incoming row'` and `'processed row'` keys
  - Worksheet errors: single-item list with `$error` key

**Behavior:**
- Reads header row (row 1) to identify columns
- Maps spreadsheet column names to model field names using `SprdsheetFlds`
- Detects and warns about duplicate columns in spreadsheet
- Skips rows with missing required columns
- Calls `cleanupfld()` for each field value
- Processes calculated fields (those with `CalculatedFld=True`)
- Tracks statistics: `num_rows`, `nRows`, `nRowsSkipped`
- Supports optional progress reporting via callback

**Example:**

```python
wb = cExcelFile.load_from_file('import.xlsx')

# Define field descriptors
field_defs = {
    'First Name': SprdsheetFldDescriptor('first_name', AllowedTypes=(str,)),
    'Last Name': SprdsheetFldDescriptor('last_name', AllowedTypes=(str,)),
    'Email': SprdsheetFldDescriptor('email', AllowedTypes=(str,)),
}

# Process the data
data = wb.save_to_listofdict(
    WksheetName='People',
    SprdsheetFlds=field_defs,
    required_columns=['first_name', 'last_name'],
    validation_callback=lambda rec: rec.get('email') is not None
)

# Separate valid from invalid records
valid_records = [d for d in data if not any(str(k).startswith('$error') for k in d)]
error_records = [d for d in data if any(str(k).startswith('$error') for k in d)]

print(f"Processed: {wb.nRows}, Skipped: {wb.nRowsSkipped}, Valid: {len(valid_records)}")
```

---

### `save_to_SQLAlchemyModel(ssnmaker, TargetModel, WksheetName, SprdsheetFlds=None, required_columns=None, progress_interval=100, progress_callback=None, validation_callback=None)`

Process spreadsheet data and save it to the database via SQLAlchemy.

**Parameters:**
- `ssnmaker` (sessionmaker): SQLAlchemy sessionmaker for database operations
- `TargetModel` (Type): The SQLAlchemy model class to populate
- `WksheetName` (str): Name of the worksheet to process
- `SprdsheetFlds` (Dict[str, SprdsheetFldDescriptor], optional): Field descriptors
- `required_columns` (list, optional): List of required model field names
- `progress_interval` (int, optional): Progress reporting interval (default: 100)
- `progress_callback` (callable, optional): Progress callback function
- `validation_callback` (callable, optional): Validation callback function

**Returns:** `Any` - List of error records (dictionaries with `$error` keys)

**Behavior:**
- Calls `save_to_listofdict()` to process spreadsheet data
- Separates valid records from error records
- Uses `Repository.bulk_add_from_listofdict()` to insert valid records into database
- Returns only error records for client handling
- Invalid/error rows are not inserted into the database

**Example:**

```python
from calvincTools.database import Repository
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///mydb.db')
Session = sessionmaker(bind=engine)

wb = cExcelFile.load_from_file('users_import.xlsx')
field_defs = {...}

errors = wb.save_to_SQLAlchemyModel(
    ssnmaker=Session,
    TargetModel=User,
    WksheetName='UserData',
    SprdsheetFlds=field_defs,
    required_columns=['first_name', 'last_name']
)

if errors:
    print(f"Import completed with {len(errors)} errors:")
    for error in errors:
        print(error)
else:
    print("Import completed successfully!")
```

---

## Usage Examples

### Example 1: Create and Save a Simple Spreadsheet

```python
from calvincTools.utils.Excel import cExcelFile

data = [
    {'Product': 'Widget', 'Price': 9.99, 'Quantity': 100},
    {'Product': 'Gadget', 'Price': 19.99, 'Quantity': 50},
    {'Product': 'Tool', 'Price': 29.99, 'Quantity': 25},
]

wb = cExcelFile()
wb.load_from_listofdict(data, wsName='Inventory')
wb.save('inventory.xlsx')
```

### Example 2: Import and Validate Spreadsheet Data

```python
from calvincTools.utils.Excel import cExcelFile

# Load existing spreadsheet
wb = cExcelFile.load_from_file('customer_import.xlsx')

# Define field validation rules
field_descriptors = {
    'Customer Name': cExcelFile.SprdsheetFldDescriptor(
        ModelFldName='name',
        AllowedTypes=(str,),
        CleanProc=lambda fld, dbfld, val, row: (True, val.strip().title() if val else None)
    ),
    'Email Address': cExcelFile.SprdsheetFldDescriptor(
        ModelFldName='email',
        AllowedTypes=(str,),
        CleanProc=validate_email  # Custom function
    ),
    'Account Status': cExcelFile.SprdsheetFldDescriptor(
        ModelFldName='status',
        AllowedTypes=(str,),
        CleanProc=lambda fld, dbfld, val, row: (val in ['Active', 'Inactive'], val)
    ),
}

# Process data
records = wb.save_to_listofdict(
    WksheetName='Customers',
    SprdsheetFlds=field_descriptors,
    required_columns=['name', 'email']
)

print(f"Total rows: {wb.nRows}")
print(f"Rows skipped: {wb.nRowsSkipped}")
```

### Example 3: Import to Database

```python
from calvincTools.database import Repository
from calvincTools.models import Customer
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
wb = cExcelFile.load_from_file('customer_data.xlsx')

errors = wb.save_to_SQLAlchemyModel(
    ssnmaker=Session,
    TargetModel=Customer,
    WksheetName='Customers',
    SprdsheetFlds=field_descriptors,
    required_columns=['name', 'email']
)

if errors:
    for error in errors:
        print(f"Row Error: {error.get('$error-row*', error)}")
```

---

## Notes and Limitations

### Current Implementation Notes

1. **Column Freezing (Partial Implementation)**
   - Header row is always frozen via `ws.freeze_panes = 'A2'`
   - The `freezecols` parameter is accepted but not yet implemented
   - TODO: Implement dynamic column freezing based on `freezecols` parameter

2. **Field Cleaning Procedure Return Values**
   - If `CleanProc` returns a tuple `(usefld, cleanval)`, both values are used
   - If `CleanProc` returns a non-tuple value, it's treated as the cleaned value (usefld determined by type checking)
   - This inconsistency could be simplified (see Improvements)

3. **Calculated Fields**
   - Fields marked with `CalculatedFld=True` are processed even if not present in spreadsheet
   - Useful for populating derived/computed fields during import
   - Must provide a `CleanProc` to generate the value

4. **Error Handling**
   - Errors during `load_from_file()` print to console; consider logging framework
   - Validation errors during `save_to_listofdict()` are embedded in returned records with `$error` prefix

5. **Performance**
   - For large files, consider using `data_only=True` in `load_from_file()` to skip formulas
   - Progress callbacks can add overhead; tune `progress_interval` accordingly

---

## Improvements and Enhancements

See the companion [Improvements Suggestions](#improvements-suggestions) section for recommended additions and refactoring.

---

## Related Classes and Functions

- **`openpyxl.Workbook`**: Parent class providing core Excel workbook functionality
- **`openpyxl.styles`**: Used for cell styling (PatternFill, Font, colors)
- **`SQLAlchemyTableModel`**: (from `calvincTools.utils.cQModels`) Used for Qt data model integration
- **`Repository`**: (from `calvincTools.database`) Used for bulk database operations
- **`cQModels.SQLAlchemyTableModel`**: Qt model wrapper for SQLAlchemy queries

---

## Error Messages and Troubleshooting

| Error Message | Cause | Solution |
|---------------|-------|----------|
| `Worksheet {name} not found in workbook.` | Specified worksheet doesn't exist | Verify worksheet name or use None for active sheet |
| `Error loading file {filename}` | File I/O or format error | Check file path, ensure file is valid XLSX format |
| `Missing required columns in spreadsheet` | Required fields not found in header | Verify spreadsheet headers match SprdsheetFlds keys |
| `Duplicate column '{name}' in spreadsheet` | Multiple columns map to same model field | Remove or rename duplicate column in spreadsheet |
| `Row {N} skipped due to validation failure.` | Validation callback returned False | Review validation logic and row data |

---

## See Also

- [openpyxl Documentation](https://openpyxl.readthedocs.io/)
- [SQLAlchemy ORM Documentation](https://docs.sqlalchemy.org/orm/)
- Related: `database.md`, `cQModels` documentation
