# utils/forms Restructure Recommendation

This document proposes a file-level restructuring for code currently in:
- calvincTools/utils/forms/cQdbFormWidgets.py
- Existing companion modules in calvincTools/utils/forms/

Scope note:
- This is a recommendation only.
- No refactor is performed in this step.

## Goals

- Keep each file focused on one cohesive responsibility.
- Reduce cognitive load from a very large multi-responsibility module.
- Make import relationships clearer and less circular.
- Improve testability by isolating UI, DB, and widget-adapter logic.

## Current Observations

The current forms package already has good separation for definitions and simple layout metadata:
- cQFormFieldDef.py
- cQFormBtnDef.py
- cQFormLayout.py
- cQFormWidgets.py

The main concentration of mixed concerns is in cQdbFormWidgets.py, which currently contains:
- low-level form element contract/base class
- field adapter widgets
- lookup widget
- UI base class for forms
- DB base class for forms
- concrete single-record and multi-record forms
- record-grid and record-list subform implementations

## Proposed Target File Set

Recommended package structure under calvincTools/utils/forms/

- __init__.py
- definitions/
  - __init__.py
  - field_def.py
  - button_def.py
  - layout_def.py
  - constants.py
- widgets/
  - __init__.py
  - base_element.py
  - field_widget.py
  - lookup_widget.py
  - name_label.py
- forms/
  - __init__.py
  - ui_base.py
  - db_base.py
  - single_record_form.py
  - multi_record_wrapper.py
- subforms/
  - __init__.py
  - record_grid.py
  - record_list_item_form.py
  - record_list.py
  - wrappers.py
- compat/
  - __init__.py
  - cQdbFormWidgets_compat.py

## Class/Code Placement Map

Move code so each file contains the following cohesive set:

1. definitions/field_def.py
- cQFormFieldDef
- cQFormFieldInstance

2. definitions/button_def.py
- cQFormBtnDef

3. definitions/layout_def.py
- cQFormLayout

4. definitions/constants.py
- cQFmConstants

5. widgets/name_label.py
- cQFmNameLabel

6. widgets/base_element.py
- cSimpRecFmElement_Base

7. widgets/field_widget.py
- cQFmFldWidg

8. widgets/lookup_widget.py
- cQFmLookupWidg

9. forms/ui_base.py
- cSRF_FormUI_Base

10. forms/db_base.py
- cSRF_Formdb_Base

11. forms/single_record_form.py
- cSRFSingleRecordForm

12. forms/multi_record_wrapper.py
- cSRFMultiRecordWrapper

13. subforms/record_grid.py
- cSRFRecordGrid

14. subforms/record_list_item_form.py
- cSRFRecordList_Record

15. subforms/record_list.py
- cSRFRecordList

16. subforms/wrappers.py
- cSRFRecordGridForm
- cSRFRecordListForm

17. compat/cQdbFormWidgets_compat.py
- transitional re-exports matching old import paths while callers migrate

## Why This Grouping "Belongs Together"

- definitions/* keeps passive metadata and schema-like dataclasses together.
- widgets/* keeps reusable UI element/adapters together.
- forms/* keeps top-level form composition and base behaviors together.
- subforms/* keeps nested/multi-record display components together.
- compat/* prevents immediate breakage while call sites move over time.

## Import Direction Recommendation

Keep import dependency one-way to avoid cycles:

- definitions -> (no dependency on forms/subforms)
- widgets -> definitions
- forms -> widgets + definitions
- subforms -> forms + widgets + definitions
- compat -> all above (re-export only)

In practice:
- avoid importing forms/* from definitions/* or widgets/*
- keep SQLAlchemy-heavy logic out of generic widget definition files where possible

## __init__.py Strategy

Recommend explicit exports only (avoid wildcard imports):

- calvincTools/utils/forms/__init__.py exports stable public API symbols.
- Subpackage __init__.py files export only intended public members.
- Keep a short, intentional surface instead of exporting entire internal modules.

## Migration Sequence (When You Decide To Refactor)

1. Create new files and move code without changing behavior.
2. Add compat/cQdbFormWidgets_compat.py with re-exports.
3. Update top-level forms __init__.py to export from new structure.
4. Update internal imports gradually module-by-module.
5. Run tests after each move cluster (widgets, then forms, then subforms).
6. Remove compat layer only after downstream imports are fully migrated.

## Optional Naming Alternative

If you want to preserve current naming style, use equivalent names:
- cQFormFieldDef.py, cQFormBtnDef.py, etc., in subfolders
- cQdbFormWidgets.py split into cSRF_FormUI_Base.py, cSRF_Formdb_Base.py, cSRFRecordGrid.py, etc.

This keeps naming continuity while still gaining separation.

## Suggested Priority Split

Highest value first:
1. Split cQdbFormWidgets.py into widgets/* + forms/* + subforms/*
2. Replace wildcard exports in forms/__init__.py with explicit exports
3. Introduce compat module for transition safety
