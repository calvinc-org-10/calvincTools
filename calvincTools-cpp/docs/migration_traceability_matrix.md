# Migration Traceability Matrix

This document is the step-1 baseline for the calvincTools C++ rewrite. It freezes the initial migration scope, identifies the authoritative Python module surface, and maps each Python module to a planned C++ component under calvincTools-cpp.

## Locked Decisions

- Strategy: full C++ rewrite target
- API direction: new C++ API first, Python compatibility later
- Validation gate: C++ tests for migrated modules
- UI direction: start Qt/C++ UI rewrite now
- New implementation files must be created under calvincTools-cpp

## Frozen Phase Scope

### Phase 1

- mathexpr_parser
- database and models abstraction
- usr_auth non-UI logic
- cMenu command system non-UI

### Phase 2

- Qt/C++ UI rewrite for menu and editor screens
- minimum viable form and widget framework required by those screens

### Phase 3

- application composition, executable targets, documentation, and cutover readiness

## Component Layout Baseline

The C++ rewrite will use these logical component areas under calvincTools-cpp.

| Planned C++ area | Purpose |
| --- | --- |
| include/calvinc_tools/core | versioning, application metadata, shared interfaces |
| include/calvinc_tools/mathexpr | math parser public API |
| include/calvinc_tools/database | models, repositories, sqlite adapters |
| include/calvinc_tools/auth | user model, password service, auth state, authorization rules |
| include/calvinc_tools/menucommand | command enum, registry, dispatch contracts |
| include/calvinc_tools/menu | menu domain objects and menu data services |
| include/calvinc_tools/ui | Qt widgets, windows, presenters/controllers |
| include/calvinc_tools/forms | form definitions, layouts, model-view adapters, widgets |
| src/app | composition root and executable startup |
| tests | C++ unit and integration tests |

## Traceability Matrix

### Package Root

| Python module | Responsibility | Planned C++ component | Phase | Status | Notes |
| --- | --- | --- | --- | --- | --- |
| calvincTools/__init__.py | package exports and version surface | include/calvinc_tools/core/package.hpp | 3 | Planned | Final exported C++ API surface defined during cutover |
| calvincTools/__version__.py | package version metadata | include/calvinc_tools/core/version.hpp and generated config | 0 | In progress | Already partially implemented in current C++ scaffold |
| calvincTools/calvincTools.py | application service locator and shared app state | include/calvinc_tools/core/application.hpp, src/app | 3 | Planned | Depends on database, auth, menucommand, and ui composition |
| calvincTools/database.py | engine setup and repository pattern | include/calvinc_tools/database, src/database | 1 | Frozen | Authoritative reference for data access behavior |
| calvincTools/models.py | core ORM schema and entities | include/calvinc_tools/database/models.hpp, src/database/models.cpp | 1 | Frozen | Recreate schema and persistence model in C++ |
| calvincTools/protocols.py | typed value and lookup contracts | include/calvinc_tools/core/protocols.hpp | 1 | Planned | Shared interface layer used by forms and lookup widgets |
| calvincTools/testmenulist.py | menu seed and test/demo data | src/menu/seed_data.cpp or tests/fixtures | 3 | Deferred | Keep out of runtime until cutover needs are clear |

### Math Expression Parser

| Python module | Responsibility | Planned C++ component | Phase | Status | Notes |
| --- | --- | --- | --- | --- | --- |
| calvincTools/mathexpr_parser/__init__.py | parser package exports | include/calvinc_tools/mathexpr/mathexpr.hpp | 1 | Frozen | Public C++ parser export surface |
| calvincTools/mathexpr_parser/eval.py | evaluator wrapper | include/calvinc_tools/mathexpr/evaluate.hpp, src/mathexpr/evaluate.cpp | 1 | Frozen | Preserve simple evaluation entry point |
| calvincTools/mathexpr_parser/math_parser.py | parser and expression semantics | include/calvinc_tools/mathexpr/parser.hpp, src/mathexpr/parser.cpp | 1 | Frozen | First behavior-parity target |

### Menu System

| Python module | Responsibility | Planned C++ component | Phase | Status | Notes |
| --- | --- | --- | --- | --- | --- |
| calvincTools/cMenu/__init__.py | menu package exports | include/calvinc_tools/menu/menu_api.hpp | 3 | Planned | Final API defined after menu and ui stabilize |
| calvincTools/cMenu/constants.py | menu layout constants | include/calvinc_tools/ui/menu_constants.hpp | 2 | Planned | UI rewrite dependency |
| calvincTools/cMenu/dbmenulist.py | menu data layer and menu records | include/calvinc_tools/menu/menu_repository.hpp, src/menu/menu_repository.cpp | 1 | Frozen | Core menu domain/data target |
| calvincTools/cMenu/menucommand_constants.py | command taxonomy and dispatch metadata | include/calvinc_tools/menucommand/command_types.hpp, src/menucommand/command_types.cpp | 1 | Frozen | Core non-UI command migration target |
| calvincTools/cMenu/cMenu.py | main Qt menu UI and navigation | include/calvinc_tools/ui/menu_window.hpp, src/ui/menu_window.cpp | 2 | Frozen for rewrite | Start Qt/C++ rewrite in phase 2 |
| calvincTools/cMenu/cEditMenu.py | menu editor UI | include/calvinc_tools/ui/menu_editor_window.hpp, src/ui/menu_editor_window.cpp | 2 | Frozen for rewrite | Depends on forms layer |

### Menu Command Handlers

| Python module | Responsibility | Planned C++ component | Phase | Status | Notes |
| --- | --- | --- | --- | --- | --- |
| calvincTools/cMenu/menucommand_handlers/__init__.py | handler package exports | include/calvinc_tools/menucommand/handlers.hpp | 2 | Planned | Final registry export surface |
| calvincTools/cMenu/menucommand_handlers/FormBrowse.py | browse form command handler | src/menucommand/handlers/form_browse_command.cpp | 2 | Planned | Depends on forms and UI layers |
| calvincTools/cMenu/menucommand_handlers/changePassword.py | password change command flow | src/menucommand/handlers/change_password_command.cpp | 2 | Planned | Depends on auth and UI layers |
| calvincTools/cMenu/menucommand_handlers/loadExternalWebPage.py | external page launch | src/menucommand/handlers/open_external_page_command.cpp | 2 | Planned | UI integration required |
| calvincTools/cMenu/menucommand_handlers/OpenTable.py | table viewer command | src/menucommand/handlers/open_table_command.cpp | 2 | Planned | Depends on data and UI layers |
| calvincTools/cMenu/menucommand_handlers/RunSQL.py | ad hoc SQL command | src/menucommand/handlers/run_sql_command.cpp | 2 | Planned | Depends on data layer and UI |

### Authentication

| Python module | Responsibility | Planned C++ component | Phase | Status | Notes |
| --- | --- | --- | --- | --- | --- |
| calvincTools/usr_auth/__init__.py | current user state helpers | include/calvinc_tools/auth/auth_context.hpp, src/auth/auth_context.cpp | 1 | Frozen | Non-UI auth target |
| calvincTools/usr_auth/models.py | user model and auth methods | include/calvinc_tools/auth/user.hpp, src/auth/user.cpp | 1 | Frozen | Core auth domain target |
| calvincTools/usr_auth/pwegg.py | password hashing and verification | include/calvinc_tools/auth/password_service.hpp, src/auth/password_service.cpp | 1 | Frozen | Select C++ crypto implementation during phase 1 |
| calvincTools/usr_auth/decorators.py | authorization guards | include/calvinc_tools/auth/authorization.hpp, src/auth/authorization.cpp | 1 | Frozen | Replace decorators with explicit service checks |
| calvincTools/usr_auth/typing.py | auth-specific typing helpers | include/calvinc_tools/auth/types.hpp | 1 | Planned | Shared aliases and small value types |
| calvincTools/usr_auth/notify.py | auth notifications | src/ui/auth_notifications.cpp | 2 | Planned | UI concern |
| calvincTools/usr_auth/ui.py | login/logout UI | include/calvinc_tools/ui/login_dialog.hpp, src/ui/login_dialog.cpp | 2 | Frozen for rewrite | Qt/C++ login surface |
| calvincTools/usr_auth/editusers.py | user management UI | include/calvinc_tools/ui/user_editor_window.hpp, src/ui/user_editor_window.cpp | 2 | Planned | Depends on auth, database, forms |
| calvincTools/usr_auth/chngPW_dlg.py | change-password dialog UI | include/calvinc_tools/ui/change_password_dialog.hpp, src/ui/change_password_dialog.cpp | 2 | Planned | Depends on auth |

### Utilities - Core

| Python module | Responsibility | Planned C++ component | Phase | Status | Notes |
| --- | --- | --- | --- | --- | --- |
| calvincTools/utils/__init__.py | utility export surface | include/calvinc_tools/core/utils.hpp | 3 | Planned | Final export set decided after module ports |
| calvincTools/utils/_calvinKlass.py | base-class helpers | include/calvinc_tools/core/base_types.hpp | 3 | Deferred | Reassess after concrete usage is known |
| calvincTools/utils/strings.py | string helpers | include/calvinc_tools/core/strings.hpp, src/core/strings.cpp | 2 | Planned | Useful support layer for forms and menu |
| calvincTools/utils/dates.py | date helpers | include/calvinc_tools/core/dates.hpp, src/core/dates.cpp | 2 | Planned | Support layer, not in frozen phase 1 |
| calvincTools/utils/misctools.py | misc helpers and function inspection | include/calvinc_tools/core/misctools.hpp, src/core/misctools.cpp | 3 | Deferred | Split and port only used parts |
| calvincTools/utils/print.py | printing helpers | include/calvinc_tools/ui/print_manager.hpp, src/ui/print_manager.cpp | 3 | Deferred | UI-dependent |
| calvincTools/utils/SQLAlcTools.py | SQLAlchemy-specific helpers | include/calvinc_tools/database/query_utils.hpp, src/database/query_utils.cpp | 1 | Planned | Port behavior, not SQLAlchemy implementation |
| calvincTools/utils/Excel.py | Excel file handling | include/calvinc_tools/core/excel.hpp, src/core/excel.cpp | 3 | Deferred | External library decision required |
| calvincTools/utils/messageBoxes.py | dialog helpers | include/calvinc_tools/ui/message_boxes.hpp, src/ui/message_boxes.cpp | 2 | Planned | UI support library |
| calvincTools/utils/fileDialogs.py | file dialog wrappers | include/calvinc_tools/ui/file_dialogs.hpp, src/ui/file_dialogs.cpp | 2 | Planned | UI support library |
| calvincTools/utils/cQModels.py | Qt data models | include/calvinc_tools/forms/qt_models.hpp, src/forms/qt_models.cpp | 2 | Planned | Forms/UI infrastructure |
| calvincTools/utils/cQWidgets.py | Qt widget extensions | include/calvinc_tools/forms/widgets.hpp, src/forms/widgets.cpp | 2 | Planned | Forms/UI infrastructure |

### Utilities - Forms Definitions

| Python module | Responsibility | Planned C++ component | Phase | Status | Notes |
| --- | --- | --- | --- | --- | --- |
| calvincTools/utils/forms/__init__.py | forms package exports | include/calvinc_tools/forms/forms_api.hpp | 2 | Planned | Export surface for form framework |
| calvincTools/utils/forms/definitions/__init__.py | definitions package exports | include/calvinc_tools/forms/definitions.hpp | 2 | Planned | Aggregate header |
| calvincTools/utils/forms/definitions/cQFormBtnDef.py | form button metadata | include/calvinc_tools/forms/button_definition.hpp, src/forms/button_definition.cpp | 2 | Planned | Needed by menu editor and forms |
| calvincTools/utils/forms/definitions/cQFormFieldDef.py | field metadata | include/calvinc_tools/forms/field_definition.hpp, src/forms/field_definition.cpp | 2 | Planned | Core form abstraction |
| calvincTools/utils/forms/definitions/cQFmConstants.py | form constants | include/calvinc_tools/forms/constants.hpp | 2 | Planned | Shared UI/forms constants |
| calvincTools/utils/forms/definitions/cQFormLayout.py | form layout builder | include/calvinc_tools/forms/form_layout.hpp, src/forms/form_layout.cpp | 2 | Planned | Key phase-2 dependency |

### Utilities - Forms Runtime

| Python module | Responsibility | Planned C++ component | Phase | Status | Notes |
| --- | --- | --- | --- | --- | --- |
| calvincTools/utils/forms/forms/__init__.py | forms runtime exports | include/calvinc_tools/forms/runtime.hpp | 2 | Planned | Aggregate header |
| calvincTools/utils/forms/forms/cSRF_FormUI_Base.py | base UI form behavior | include/calvinc_tools/forms/form_ui_base.hpp, src/forms/form_ui_base.cpp | 2 | Planned | Core runtime foundation |
| calvincTools/utils/forms/forms/cSRF_Formdb_Base.py | DB-backed form behavior | include/calvinc_tools/forms/form_db_base.hpp, src/forms/form_db_base.cpp | 2 | Planned | Depends on database layer |
| calvincTools/utils/forms/forms/cSRFSingleRecordForm.py | single-record form | include/calvinc_tools/forms/single_record_form.hpp, src/forms/single_record_form.cpp | 2 | Planned | Core phase-2 form target |
| calvincTools/utils/forms/forms/cSRFMultiRecordWrapper.py | multi-record wrapper | include/calvinc_tools/forms/multi_record_wrapper.hpp, src/forms/multi_record_wrapper.cpp | 2 | Planned | Needed for menu editor and admin flows |

### Utilities - Forms Subforms

| Python module | Responsibility | Planned C++ component | Phase | Status | Notes |
| --- | --- | --- | --- | --- | --- |
| calvincTools/utils/forms/subforms/__init__.py | subforms export surface | include/calvinc_tools/forms/subforms.hpp | 2 | Planned | Aggregate header |
| calvincTools/utils/forms/subforms/cSRFRecordList.py | list subform | include/calvinc_tools/forms/record_list.hpp, src/forms/record_list.cpp | 2 | Planned | Depends on forms runtime and models |
| calvincTools/utils/forms/subforms/cSRFRecordGrid.py | grid subform | include/calvinc_tools/forms/record_grid.hpp, src/forms/record_grid.cpp | 2 | Planned | Depends on forms runtime and models |

### Utilities - Forms Widgets

| Python module | Responsibility | Planned C++ component | Phase | Status | Notes |
| --- | --- | --- | --- | --- | --- |
| calvincTools/utils/forms/widgets/__init__.py | widget exports | include/calvinc_tools/forms/widget_api.hpp | 2 | Planned | Aggregate header |
| calvincTools/utils/forms/widgets/cSimpRecFmElement_Base.py | base record-form widget | include/calvinc_tools/forms/simple_record_element_base.hpp, src/forms/simple_record_element_base.cpp | 2 | Planned | Widget foundation |
| calvincTools/utils/forms/widgets/cQFmNameLabel.py | field label widget | include/calvinc_tools/forms/name_label.hpp, src/forms/name_label.cpp | 2 | Planned | Widget support |
| calvincTools/utils/forms/widgets/cQFmLookupWidg.py | lookup widget | include/calvinc_tools/forms/lookup_widget.hpp, src/forms/lookup_widget.cpp | 2 | Planned | Depends on lookup protocols and database |
| calvincTools/utils/forms/widgets/cQFmFldWidg.py | field widget | include/calvinc_tools/forms/field_widget.hpp, src/forms/field_widget.cpp | 2 | Planned | Widget support |

## Deferred and Legacy Review

The following items are recognized but not part of the frozen phase-1 implementation set.

| Item | Decision |
| --- | --- |
| testmenulist.py | defer until runtime seeding/test fixture needs are clearer |
| Excel.py | defer until external library choice is made |
| print.py | defer until core UI flows exist |
| misctools.py | split and port only concrete dependencies |
| _calvinKlass.py | reassess after real C++ inheritance needs are visible |

## Acceptance Criteria For Step 1

- the Python package surface is inventoried in one place
- every Python module has a planned C++ destination or an explicit deferral decision
- phase-1 targets are frozen and identifiable
- the current C++ scaffold remains the baseline for versioning and project structure
