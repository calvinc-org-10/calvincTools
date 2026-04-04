# calvincTools Architecture and cSRF Developer Notes (Draft 02)

This document expands on the notes in draft01 and maps them to the current code in the calvincTools 2.x rewrite.

## 1) What calvincTools provides

At a high level, calvincTools is a PySide6 + SQLAlchemy toolkit centered around:

- A database-driven menu runtime (`cMenu`) and command handlers
- A form framework for CRUD-style forms (`cSRF*` classes)
- Reusable widget wrappers/adapters and utility helpers
- An application hook singleton (`cTools_apphooks`) used as a service locator

Key package modules:

- `apphooks.py`: global app initialization hooks
- `database.py`: SQLite engine/sessionmaker and generic repository
- `models.py`: core ORM models (`menuGroups`, `menuItems`, etc.)
- `dbmenulist.py`: menu record access helpers
- `cMenu.py`: menu UI and menu command dispatch
- `menucommand_handlers.py`: handlers/forms invoked by menu commands
- `utils/forms/...`: cSRF form framework (definitions, widgets, forms, subforms)

## 2) Startup and required initialization

The form and menu runtime expect `cTools_apphooks` to be initialized before use.

`cTools_apphooks.initialize(...)` accepts:

- `app_sessionmaker`
- `FormNameToURL_Map`
- `ExternalWebPageURL_Map`
- `appver`

Typical runtime dependency flow:

1. Host app creates SQLAlchemy engine/sessionmaker
2. Host app defines form routing maps
3. Host app calls `cTools_apphooks.initialize(...)`
4. UI creates `cMenu(...)`
5. `cMenu` reads menu rows and dispatches commands

Notes:

- `cMenu.__init__` immediately fetches hooks from `cTools_apphooks`.
- Missing hook initialization raises runtime errors through getter guards.

## 3) Menu system overview

### 3.1 Data model and persistence

The menu system is backed by:

- `menuGroups` (group metadata)
- `menuItems` (menu rows and options)

`models.py` ensures tables exist on import and seeds starter data.

`dbmenulist.MenuRecords` provides menu-centric access helpers:

- `dfltMenuGroup()`
- `dfltMenuID_forGroup(mGroup)`
- `menuExist(mGroup, mID)`
- `menuDict(mGroup, mID)`
- `menuGroupsDict()`
- `menuListDict(mGroup)`

### 3.2 Command dispatch

`menucommand_constants.py` defines:

- `MENUCOMMANDS` numeric map
- `COMMANDNUMBER` namespace helper

`cMenu.handleMenuButtonClick()` maps command numbers to behavior including:

- `LoadMenu`
- `FormBrowse`
- `OpenTable`
- `RunSQLStatement`
- `LoadExtWebPage`
- `EditMenu`
- `ExitApplication`

Unimplemented known commands show informational dialogs.

### 3.3 Form routing from menu

`menucommand_handlers.FormBrowse(...)` resolves `formname` via `FormNameToURL_Map` and then:

- invokes mapped view/form callable when present, or
- displays an under-construction dialog

`cMenu` tracks child windows by ID to avoid duplicate opens.

## 4) cSRF framework: class roles

Your draft01 call-flow notes match current code in `utils/forms`.

### 4.1 Core split

- `cSRF_FormUI_Base`: UI composition, field/widget creation, pages, button hook points
- `cSRF_Formdb_Base`: ORM model/sessionmaker/current-record plumbing

### 4.2 Main concrete form flavors

- `cSRFSingleRecordForm`:
  - combines UI + DB base classes
  - full CRUD-like workflow with record navigation
  - default action buttons (first/prev/next/last/add/save/delete/cancel)

- `cSRFMultiRecordWrapper`:
  - UI-only wrapper form
  - intended container for subforms such as list/grid record views (see 4.3)

- `cSRFRecordGridForm` and `cSRFRecordListForm` currently exist as placeholders subclassing `cSRFMultiRecordWrapper`.

### 4.3 Subforms

- `cSRFRecordGrid`:
  - table-based subform (QTableView + SQLAlchemyTableModel)
  - supports parent-linked filtering and add/delete rows

- `cSRFRecordList_Record`:
  - single record form element used inside record-list displays

- `cSRFRecordList`:
  - list-based multi-record subform (`QListWidget`)

## 5) cSRF initialization sequence (verified)

The following sequence in `cSRF_FormUI_Base.__init__` is accurate and central:

1. Resolve field definitions source:
   - class attr `_field_defs`, else incoming `field_defs`, else `defineFields()`
2. `_validate_field_defs()`
3. Build base layout via `_buildFormLayout()`
4. `_buildPages()`
5. `_build_fields()`
6. `_addActionButtons()`
7. `initialdisplay()`

Your draft01 pseudo-code for `_build_fields()` is correct:

```python
_build_fields()
    for defn in self._field_defs:
        widget = self._create_widget(defn)
        self._configure_widget(widget, defn)
        self._connect_widget(widget, defn)
        self._place_widget(widget, defn)
```

## 6) Field and button definition APIs

### 6.1 `cQFormFieldDef`

Defined in `utils/forms/definitions/cQFormFieldDef.py` as a dataclass.

Important properties:

- `name`
- `field_type` (`SCALAR`, `LOOKUP`, `SUBFORM`, `INTERNAL`)
- `widget_type`
- `label`, `label_alignment`
- `page`, `position`
- `choices`, `initval`
- behavior hooks: `transform`, `on_change`
- UI options: `readonly`, `tooltip`, size, color, focus policy

Runtime storage:

- `cQFormFieldInstance(definition, widget)`

### 6.2 `cQFormBtnDef`

Button definitions support:

- `text`, `icon`, `action`, `commitBtn`
- section markers via `ButtonType`:
  - `NORMAL`
  - `NEW_HSECTION`
  - `NEW_VSECTION`

### 6.3 `cQFormLayout`

Structured layout object returned by `_buildFormLayout()`:

- `main`, `header`, `form`
- `fixed_top`, `pages`, `fixed_bottom`
- `buttons`, `status_bar`
- optional UI refs: `lblFormName`, `newrecFlag`

## 7) cSRF page semantics

`FormPage(idx)` resolves to a `QGridLayout` by:

- page name (`str`)
- page index (`int`)
- special enum (`cQFmConstants`) for fixed regions:
  - fixed top
  - fixed bottom

If `pages` is empty, framework defaults to a single page `Main`.

## 8) Single-record lifecycle details

In `cSRFSingleRecordForm`:

- `initialdisplay()` calls:
  - `initializeRec()`
  - `on_loadfirst_clicked()`

Navigation helpers:

- `on_loadfirst_clicked`, `on_loadprev_clicked`, `on_loadnext_clicked`, `on_loadlast_clicked`

Safety behavior:

- `isit_OKToLeaveRecord()` prompts when dirty
- supports Save / Discard / Cancel path before navigation

Record loading and persistence style:

- database reads use short sessions
- loaded objects are expunged (detached)
- commit operations use merge/add within fresh sessions

## 9) Current cSRF hierarchy/dependency 

| class | description | inherits from (in cSRF classes) | may have components or attributes of class |
|---|---|---|---|
| cQFmConstants | constants |  |  |
| cQFormLayout | form layout definitions |  | cQFmNameLabel |
| cQFormFieldDef | form field definitions |  |  |
| cQFormFieldInstance | runtime field def + widget |  | cQFormFieldDef, QWidget (usually a descendant of cSimpleRecFmElement_Base) |
| cQFormBtnDef | form button definitions |  |  |
| cQFmNameLabel | form name label |  |  |
| cSimpRecFmElement_Base | form field base class |  |  |
| cQFmFldWidg | form field (data entry) | cSimpRecFmElement_Base | cComboBoxFromDict, cDataList |
| cQFmLookupWidg | form field for db lookup | cSimpRecFmElement_Base | cComboBoxFromDict, cDataList |
| cSRF_FormUI_Base | form base class (UI) |  | cComboBoxFromDict, cDataList, cQFormLayout,  cQFormFieldDef, cQFormFieldInstance, cQFormBtnDef, cQFmFldWidg, cQFmLookupWidg |
| cSRF_Formdb_Base | form base class (db) |  | calvincTools.utils.SQLAlcTools.get_primary_key_column |
| cSRFSingleRecordForm | single record form | cSRF_FormUI_Base, cSRF_Formdb_Base | cQFormLayout, cQFormFieldDef, cQFormBtnDef, cQFmNameLabel, cSimpRecFmElement_Base from calvincTools.utils.cQWidgets import cGridWidget, cstdTabWidget from calvincTools.utils.messageBoxes import areYouSure |
| cSRFMultiRecordWrapper | wrapper form for subforms  (no "parent" record on this form) | cSRF_FormUI_Base | cQFormLayout, cQFormFieldDef, cQFormBtnDef, cQFmNameLabel from calvincTools.utils.cQWidgets import cGridWidget, cstdTabWidget |
| cSRFRecordGrid | subform, table display supports parent record (cSSRFSingleRecordForm) or not (cSRFMultiRecordWrapper) | cSRF_Formdb_Base, cSimpRecFmElement_Base | from calvincTools.utils.cQModels import SQLAlchemyTableModel  from calvincTools.utils.SQLAlcTools import get_primary_key_column |
| cSRFRecordGridForm  (placeholder) | cSRFMultiRecordWrapper + cSRFRecordGrid | cSRFMultiRecordWrapper |  |
| cSRFRecordList_Record | single db record presented by cSRFRecordList | cSRF_Formdb_Base, cSRF_FormUI_Base |  |
| cSRFRecordList | subform, multiple record/form display supports parent record (cSSRFSingleRecordForm) or not (cSRFMultiRecordWrapper) | cSRFSingleRecordForm | cSRFRecordList_Record |
| cSRFRecordListForm (placeholder) | cSRFMultiRecordWrapper + cSRFRecordList | cSRFMultiRecordWrapper |  |

## 10) Minimal subclassing recipe

For a new single-record form:

1. Subclass `cSRFSingleRecordForm`
2. Provide model/sessionmaker (class attrs or constructor)
3. Implement `defineFields()` returning `list[cQFormFieldDef]`
4. Optionally override `defineActionButtons()` and/or `_addActionButtons()`
5. Register form in app `FormNameToURL_Map`
6. Initialize apphooks before opening menu

Skeleton:

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

## 11) Practical caveats in current codebase

Items to remember while extending:

- Some docs in `docs/` reference older names (`cSimpleRecord*`, `cQdbFormWidgets`) from pre-rewrite structure.
- `cSRFRecordGridForm` and `cSRFRecordListForm` are currently placeholders.
- `cSRFRecordList.del_row()` is marked TODO/incomplete.
- Several modules include TODO comments and evolving APIs; prefer testing concrete behavior when integrating.

## 12) Suggested documentation follow-ups

To mature this draft into formal docs:

- Add end-to-end example app showing `cTools_apphooks.initialize` + `cMenu`
- Add one complete custom `cSRFSingleRecordForm` example with lookup and subform fields
- Add explicit migration note: old `cSimpleRecord*` naming to `cSRF*`
- Document public/stable API surface vs internal implementation modules

---

This draft intentionally captures both current architecture and in-progress areas so form/menu customization work can proceed with realistic expectations.