# calvincTools Architecture and Developer Notes (Draft 03)

This document revises and expands draft02.

Goals of this update:

- Keep the solid cMenu + cSRF coverage from draft02
- Improve organization and implementation-level accuracy
- Add missing documentation for non-form utilities under `utils/`
- Explicitly ignore deprecated-area code for this draft

Scope note:

- This draft intentionally does **not** document code in deprecated folders (for example, `deprecated code` / `code to deprecate`).
- Notes below are based on active modules in the current 2.x rewrite branch.

## Quick reference: API stability and intent

Stability labels used in this draft:

- **Public (stable)**: Intended for regular app usage in this branch; low expected churn.
- **Public (provisional)**: Usable now, but shape/behavior may still evolve.
- **Internal**: Helper/scaffolding/prototype surface; avoid depending on it as external API.

| Area | Primary modules/classes | Stability | Notes |
|---|---|---|---|
| App init and service locator | `apphooks.py`, `cTools_apphooks.initialize` | Public (stable) | Required startup wiring for menu/form runtime |
| Menu runtime and dispatch | `cMenu.py`, `menucommand_handlers.py`, `dbmenulist.py` | Public (stable) | Core runtime entry points |
| Form framework core | `utils/forms` (`cSRFSingleRecordForm`, defs/layout classes) | Public (provisional) | Main extension surface; still under rewrite |
| ORM/query helpers | `utils/SQLAlcTools.py` | Public (provisional) | Useful low-level helpers, some call-site caution needed |
| Qt data models | `utils/cQModels.py` | Public (provisional) | Widely useful, still evolving behaviors |
| Generic Qt widgets/layout helpers | `utils/cQWidgets.py` | Public (provisional) | Reusable building blocks |
| Dialog/file picker helpers | `utils/messageBoxes.py`, `utils/fileDialogs.py` | Public (stable) | UI convenience utilities |
| Export/print helpers | `utils/Excel.py`, `utils/print.py` | Public (provisional) | Export path active; upload base class incomplete |
| String/misc helpers | `utils/strings.py`, `utils/misctools.py` | Public (stable) | Utility-level helpers |
| Date helper module | `utils/calvindate.py` | Internal (deprecated) | Legacy class removed; parse helpers still present |
| Prototype scaffold | `utils/_calvinKlass.py` | Internal | Placeholder only |

## 1) What calvincTools provides

At a high level, calvincTools is a PySide6 + SQLAlchemy toolkit centered around:

- A database-driven menu runtime (`cMenu`) and command handlers
- A form framework for CRUD-style forms (`cSRF*` classes)
- Reusable widget/model/util helpers under `utils/`
- An app hook singleton (`cTools_apphooks`) used as a service locator

Primary package modules:

- `apphooks.py`: app-level dependency registration
- `database.py`: engine/sessionmaker helpers and DB plumbing
- `models.py`: ORM models for menu metadata
- `dbmenulist.py`: menu record access helper layer
- `cMenu.py`: menu UI and command dispatch
- `menucommand_handlers.py`: handlers used by command dispatch
- `utils/forms/...`: cSRF form system

Stability:

- App hooks/menu surface: **Public (stable)**
- Form framework in rewrite areas: **Public (provisional)**

## 2) Startup and required initialization

The menu/form runtime assumes app hooks are initialized before menu-driven form actions run.

`cTools_apphooks.initialize(...)` accepts:

- `app_sessionmaker`
- `FormNameToURL_Map`
- `ExternalWebPageURL_Map`
- `appver`

Typical dependency flow:

1. Host app creates SQLAlchemy engine/sessionmaker
2. Host app defines form and external URL maps
3. Host app calls `cTools_apphooks.initialize(...)`
4. UI instantiates `cMenu(...)`
5. Menu commands resolve handlers/forms using hooks

Operational note:

- `cMenu.__init__` pulls dependencies from `cTools_apphooks` early.
- Missing initialization surfaces as runtime errors from hook getters.

## 3) Menu system overview

Stability: **Public (stable)**

### 3.1 Persistence model and records

The menu subsystem is backed by:

- `menuGroups`
- `menuItems`

`dbmenulist.MenuRecords` provides query helpers including:

- `dfltMenuGroup()`
- `dfltMenuID_forGroup(mGroup)`
- `menuExist(mGroup, mID)`
- `menuDict(mGroup, mID)`
- `menuGroupsDict()`
- `menuListDict(mGroup)`

### 3.2 Command dispatch

`menucommand_constants.py` defines command constants (`MENUCOMMANDS`, `COMMANDNUMBER`).

`cMenu.handleMenuButtonClick()` routes command numbers to actions such as:

- `LoadMenu`
- `FormBrowse`
- `OpenTable`
- `RunSQLStatement`
- `LoadExtWebPage`
- `EditMenu`
- `ExitApplication`

Unimplemented commands typically show a user-facing placeholder dialog.

### 3.3 Form routing from menu

`menucommand_handlers.FormBrowse(...)` resolves form names through `FormNameToURL_Map` and either:

- invokes the mapped callable/form, or
- shows an under-construction message if no live target exists

`cMenu` also tracks child windows by ID to reduce duplicate opens.

## 4) cSRF framework: class roles

Stability: **Public (provisional)**

### 4.1 Core split

- `cSRF_FormUI_Base`: layout/pages/widget construction, signal wiring, button areas
- `cSRF_Formdb_Base`: ORM model/sessionmaker/current-record handling

### 4.2 Main form flavors

- `cSRFSingleRecordForm`
  - combines UI + DB base classes
  - implements single-record navigation and CRUD-style actions
  - includes default action buttons (first/prev/next/last/add/save/delete/cancel)

- `cSRFMultiRecordWrapper`
  - UI wrapper shell for subform-oriented multi-record views

- `cSRFRecordGridForm` and `cSRFRecordListForm`
  - currently placeholder subclasses of `cSRFMultiRecordWrapper`

### 4.3 Subforms

- `cSRFRecordGrid`
  - table-style subform built around `QTableView` + `SQLAlchemyTableModel`
  - supports parent-linked filtering and row add/delete flows

- `cSRFRecordList_Record`
  - single-record display/edit unit used inside list-style compositions

- `cSRFRecordList`
  - list-driven multi-record subform (`QListWidget` based)

## 5) cSRF initialization sequence

`cSRF_FormUI_Base.__init__` sequence is central to extension points:

1. Resolve field definitions source:
   - class `_field_defs`, else constructor `field_defs`, else `defineFields()`
2. `_validate_field_defs()`
3. `_buildFormLayout()`
4. `_buildPages()`
5. `_build_fields()`
6. `_addActionButtons()`
7. `initialdisplay()`

Field build loop shape:

```python
_build_fields()
    for defn in self._field_defs:
        widget = self._create_widget(defn)
        self._configure_widget(widget, defn)
        self._connect_widget(widget, defn)
        self._place_widget(widget, defn)
```

## 6) Field/button/layout definition APIs

### 6.1 `cQFormFieldDef`

Dataclass representing a form field definition.

Important members include:

- `name`
- `field_type` (`SCALAR`, `LOOKUP`, `SUBFORM`, `INTERNAL`)
- `widget_type`
- `label`, `label_alignment`
- `page`, `position`
- `choices`, `initval`
- behavior hooks (`transform`, `on_change`)
- UI options (`readonly`, `tooltip`, size, color, focus policy)

Runtime binding is stored via `cQFormFieldInstance(definition, widget)`.

### 6.2 `cQFormBtnDef`

Defines action button metadata including:

- `text`, `icon`, `action`, `commitBtn`
- section markers (`ButtonType.NORMAL`, `NEW_HSECTION`, `NEW_VSECTION`)

### 6.3 `cQFormLayout`

Structured return object from `_buildFormLayout()` containing key regions:

- `main`, `header`, `form`
- `fixed_top`, `pages`, `fixed_bottom`
- `buttons`, `status_bar`
- optional refs (`lblFormName`, `newrecFlag`)

## 7) Page semantics

`FormPage(idx)` resolves a `QGridLayout` using:

- page name (`str`)
- page index (`int`)
- fixed-region constants (`cQFmConstants`)

When no explicit pages are defined, the framework uses a default single page (`Main`).

## 8) Single-record lifecycle details

In `cSRFSingleRecordForm`:

- `initialdisplay()` calls `initializeRec()` then `on_loadfirst_clicked()`
- navigation handlers include first/prev/next/last helpers
- `isit_OKToLeaveRecord()` prompts on dirty-state transitions
- save/discard/cancel paths are enforced before record changes

Persistence style in this branch:

- read operations use short-lived sessions
- loaded entities are often detached (`expunge`) for UI-side editing
- save paths use merge/add in fresh sessions

## 9) Known caveats in current codebase

- Some docs still reference older pre-rewrite names (`cSimpleRecord*`, `cQdbFormWidgets`).
- `cSRFRecordGridForm` and `cSRFRecordListForm` are placeholders.
- `cSRFRecordList.del_row()` is marked TODO/incomplete.
- Some APIs are still evolving; verify behavior with focused tests when integrating.

## 10) Additional utils documentation (non-form)

This section covers active modules under `utils/` beyond the forms subsystem.

### 10.1 `utils/SQLAlcTools.py`

Stability: **Public (provisional)**

Core SQLAlchemy helper functions:

- `recordsetList(tbl, retFlds=..., where=None, orderby=None, ssnmaker=None) -> list`
  - Executes a select against table/model/query source
  - Returns list of mapping rows when `ssnmaker` is provided
  - Supports wildcard/all-field behavior and optional textual where/order clauses

- `get_table_object(obj) -> Table`
  - Resolves ORM model class or core table to the underlying table object

- `select_with_join_excluding(left, right, on_clause, exclude_from_right=None) -> Select`
  - Join helper selecting all left columns + filtered right columns

- `select_join_auto_exclude(tables, on_clauses, exclude=None) -> Select`
  - Multi-join helper deduplicating repeated column names across joined tables

- `get_primary_key_column(model) -> Any`
  - Enforces a single-column PK model and returns that column

Usage caveats:

- `recordsetList` uses textual SQL fragments for `where`/`orderby`; callers should ensure safe input.
- `select_join_auto_exclude` validates each join clause is a SQLAlchemy `ClauseElement`.

### 10.2 `utils/cQModels.py`

Stability: **Public (provisional)**

Qt model adapters for dict/ORM/SQL use:

- `cDictModel(QAbstractTableModel)`
  - Two-column key/value table model over a Python dict
  - Value column editable via `setData`

- `SQLAlchemyTableModel(QAbstractTableModel)`
  - ORM-backed editable table model
  - Key methods:
    - `refresh(filter=None, orderby=None)`
    - `setData(..., persist=False)`
    - `save_changes()`
    - `insertRow(..., persist=False)`
    - `removeRow(...)`
    - `record(row=None)`
    - `findData`, `findColumn`
    - `getDataAsList`, `getDataAsDict`
    - `getSQLStatement`
    - dirty-state helpers `isDirty`, `clearDirty`

- `SQLAlchemySQLQueryModel(QAbstractTableModel)`
  - Read-only model over raw SQL query results
  - Provides `refresh`, `query`, `record`, `colIndex`
  - `save_changes` intentionally warns that direct persistence is unsupported

Practical behavior notes:

- `SQLAlchemyTableModel` configures an internal session factory with `expire_on_commit=False`.
- Detached-object editing is used, then merged/added back for persistence.

### 10.3 `utils/cQWidgets.py`

Stability: **Public (provisional)**

General reusable UI widgets/layout helpers:

- `cDataList(QLineEdit)`
  - Completer-backed free text selector over dictionary values
  - `selectedItem()` returns matching keys and current text
  - `addChoices` and `setChoice` update/resolve selection set

- `cComboBoxFromDict(QComboBox)`
  - Populates combo entries from dict key/value pairs
  - `replaceDict` replaces all options

- `cQRecordsetView(QWidget)`
  - Scrollable record container with optional “Add” button
  - Useful for stacked record widgets and dynamic row insertion

- `clearLayout(layout, keepItems=None)`
  - Recursive layout cleanup preserving specified items

- `cstdTabWidget() -> QTabWidget`
  - Standardized tab widget initialization

- `cGridWidget(QWidget)`
  - Grid container wrapper with optional scroll area
  - Exposes/forwards grid APIs (`addWidget`, `addLayout`, etc.)

### 10.4 `utils/fileDialogs.py`

Stability: **Public (stable)**

- `cFileSelectWidget(QWidget)`
  - Composite widget with a choose/drop button + chosen-file label
  - Supports drag-and-drop file URLs and click-to-open dialog
  - Emits `fileChosen` signal when a file is confirmed
  - `getFileChosen()` returns current selected path text

### 10.5 `utils/messageBoxes.py`

Stability: **Public (stable)**

Dialog helpers:

- `pleaseWriteMe(addlmessage, parent)`
  - Warning dialog for not-yet-implemented features

- `areYouSure(parent, title, question, answerChoices=..., dfltAnswer=...)`
  - Confirmation helper around `QMessageBox.question`

- `UnderConstruction_Dialog(QDialog)`
  - Standard “not built yet” dialog with SVG asset

Also defines standard sizes:

- `std_windowsize`
- `std_popdialogsize`

### 10.6 `utils/Excel.py`

Stability: **Public (provisional)**

Excel export/upload support:

- `Excelfile_fromqs(qset, flName=None, freezecols=0, returnFileName=False)`
  - Accepts `QAbstractTableModel` (including `SQLAlchemyTableModel`) or list of dicts
  - Builds workbook with bold/gray header row and frozen top row
  - Returns workbook object or filename depending on `returnFileName`

- `UpldSprdsheet`
  - Base class scaffolding for spreadsheet upload validation/cleanup
  - Includes field descriptor helper and cleanup method
  - `process_spreadsheet(...)` currently stubbed (`pass`)

### 10.7 `utils/strings.py`

Stability: **Public (stable)**

String conversion helpers:

- `str2(s, TypeTransforms=None, ValueTransforms=None)`
  - Value transform precedence over type transforms
  - Default behavior converts `None` to `""`

- `WrapInQuotes`, `UnWrapQuotes`, `IsWrappedInQuotes`

### 10.8 `utils/misctools.py`

Stability: **Public (stable)**

- `is_hashable(obj) -> bool`
  - Utility used by other helpers (for example `str2`)

- `show_fns(path_) -> dict`
  - AST-based extraction of module-level classes/functions and method summaries

- `pretty_show_fns(path_) -> str`
  - Formatted text wrapper over `show_fns`

### 10.9 `utils/print.py`

Stability: **Public (provisional)**

- `cPrintManager`
  - Printing/preview/PDF export manager for widgets and scroll-area content
  - Methods:
    - `open_preview()`
    - `export_pdf()`
    - `handle_print(printer)`

Implementation note:

- Rendering uses per-page `QImage` slices scaled to printer page width to support long widgets.

### 10.10 `utils/calvindate.py`

Stability: **Internal (deprecated)**

Status in current code:

- `calvindate` class constructor raises `DeprecationWarning` in `__new__` and should be treated as removed/deprecated.

Still-available helper functions in module:

- `IsDateString`
- `parse_relative_time`
- `extract_date_from_text`
- `parse_flexible_date`
- `parse_duration`
- `parse_iso_week_date`

Recommendation:

- Prefer direct `datetime` + `dateutil` usage for new code.

### 10.11 `utils/_calvinKlass.py`

Stability: **Internal**

- Prototype skeleton class (`_calvinKlass`) only.
- No current runtime utility behavior beyond placeholder structure.

## 11) Minimal subclassing recipe (single-record form)

1. Subclass `cSRFSingleRecordForm`
2. Provide model/sessionmaker (class attrs or constructor)
3. Implement `defineFields()` returning `list[cQFormFieldDef]`
4. Optionally override `defineActionButtons()` and/or `_addActionButtons()`
5. Register form in `FormNameToURL_Map`
6. Ensure apphooks initialization before opening menu/forms

Example skeleton:

```python
class MyForm(cSRFSingleRecordForm):
    _formname = "My Form"
    _ORMmodel = MyModel
    _ssnmaker = MySessionmaker
    pages = ["Main", "Advanced"]

    def defineFields(self):
        return [
            cQFormFieldDef(name="name", label="Name", page="Main", position=(0, 0)),
            cQFormFieldDef(name="active", label="Active", page="Main", position=(1, 0)),
        ]
```

## 12) Recommended import surface

Use this section as practical guidance for app code consuming calvincTools.

Recommended direct imports (lowest risk in current branch):

- Menu/runtime entry points used by host apps (`cMenu`, menu command handlers, apphooks initialization)
- cSRF base/form classes intended for subclassing (`cSRFSingleRecordForm`, field/layout/button definition classes)
- Utility helpers with stable behavior (`strings`, `misctools`, dialog/file helper widgets)

Use with caution (provisional but useful):

- `utils/SQLAlcTools.py` query/join helper functions
- `utils/cQModels.py` model adapters, especially editable ORM-table model flows
- `utils/cQWidgets.py` higher-level composite widgets/layout wrappers
- `utils/Excel.py` export function and upload base scaffolding
- `utils/print.py` printing manager

Avoid as import targets for new app code:

- `utils/calvindate.py` class-based date wrapper (`calvindate`) because it is deprecated/removed
- `utils/_calvinKlass.py` prototype scaffold
- Anything under deprecated folders (`deprecated code`, `code to deprecate`)

Import style guidance:

- Prefer importing concrete symbols from explicit modules over broad wildcard imports.
- Avoid depending on incidental re-export behavior from package `__init__.py` files when long-term stability matters.
- For provisional modules, isolate usage behind your own app-level adapter functions to reduce churn during upgrades.

## 13) Suggested next doc steps

- Add one complete end-to-end host app sample (`initialize` + `cMenu` + one routed form)
- Add one complete `cSRFSingleRecordForm` example with lookup and subform fields
- Publish migration map from old `cSimpleRecord*` naming to `cSRF*`
- Mark stable/public API surface vs internal/subject-to-change modules

---

Draft 03 is intended as a practical developer-facing map for current active code, with placeholders and deprecated areas explicitly called out.
