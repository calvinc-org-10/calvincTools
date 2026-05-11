## Plan: Full calvincTools C++ Rewrite

Full package migration will proceed as a staged Qt/C++ rewrite centered in calvincTools-cpp, with new files created only under calvincTools-cpp, a new C++-first API, and C++-native tests as the acceptance gate for each migrated area.

**Steps**
1. Phase 0 - Baseline and architecture lock: confirm authoritative module map from Python package and freeze migration targets for Phase 1 (mathexpr_parser, database/models abstraction, usr_auth non-UI logic, cMenu command system non-UI) and in-scope UI rewrite. Establish a migration traceability matrix mapping each Python module to planned C++ component. *blocks all later steps*
2. Phase 0 - Build foundation in calvincTools-cpp: extend CMake to support modular targets (core, data, auth, menu, ui), add install rules, add strict compiler settings, and add test integration scaffolding. Keep current version source mechanism as single source in CMake. *depends on 1*
3. Phase 0 - Testing harness: create C++ test runner and test directory structure under calvincTools-cpp/tests, define per-module test conventions, and wire tests into CMake/CTest. C++ tests are the required gate per your decision. *depends on 2*
4. Phase 1 - Core parser migration: port mathexpr_parser parser/evaluator into calvincTools-cpp/src/mathexpr with public headers in calvincTools-cpp/include/calvinc_tools/mathexpr. Include operator precedence, functions/constants parity tests, and error-handling behavior tests. *depends on 3*
5. Phase 1 - Data layer migration: implement SQLite-backed data access abstraction for menu and app models in calvincTools-cpp/src/database and calvincTools-cpp/include/calvinc_tools/database. Recreate model structures and repository/query patterns currently handled by SQLAlchemy. *depends on 3; parallel with 4 after shared interfaces are fixed*
6. Phase 1 - Auth logic migration (non-UI): implement user entity, password hashing/verification service, session/auth state service, and authorization checks in calvincTools-cpp/src/auth and include equivalents. Keep this layer UI-agnostic and callable by both command and UI layers. *depends on 5 for user persistence*
7. Phase 1 - Menu command engine migration (non-UI): migrate command constants/enum, command registry, and dispatch execution into calvincTools-cpp/src/menucommand. Preserve semantic command categories from Python while designing typed C++ command contracts. *depends on 5 and 6*
8. Phase 2 - Qt/C++ UI rewrite start: create Qt-based equivalents for cMenu and cEditMenu in calvincTools-cpp/src/ui with include counterparts, including signal/slot flows for login/logout/shutdown and menu navigation wiring. *depends on 7; can begin partially in parallel after 5 for read-only screens*
9. Phase 2 - Form and widget framework migration: recreate minimum viable form framework needed by cMenu/cEditMenu workflows (field definition, layout orchestration, model-view adapters), then incrementally port advanced widgets. *depends on 8*
10. Phase 3 - App composition and executable target: add application composition root that wires database, auth, command engine, and UI into executable/library targets under calvincTools-cpp/src/app. Define startup configuration, resource loading, and runtime error/reporting strategy. *depends on 8 and 9*
11. Phase 3 - Documentation and developer workflow: expand calvincTools-cpp/README.md with build/run/test matrix, architecture map, and migration status table. Add contributor guidance for adding new modules/tests in the C++ tree. *depends on 10*
12. Phase 3 - Cutover readiness and deprecation plan: define feature-completeness checklist against Python modules, identify remaining unmigrated areas, and produce cutover criteria for adopting the C++ app as primary implementation. *depends on 11*

**Relevant files**
- F:/calvincTools/calvincTools-cpp/CMakeLists.txt — modular targets, test integration, install rules, compiler and dependency policy
- F:/calvincTools/calvincTools-cpp/README.md — migration status, build/run/test workflow, architecture notes
- F:/calvincTools/calvincTools-cpp/include/calvinc_tools/version.hpp — keep API/version conventions consistent as project expands
- F:/calvincTools/calvincTools-cpp/src/version.cpp — retain package/version identity behavior while adding modules
- F:/calvincTools/calvincTools-cpp/include/calvinc_tools/version_config.hpp.in — preserve generated version source
- F:/calvincTools/calvincTools/mathexpr_parser/math_parser.py — reference behavior parity for parser semantics
- F:/calvincTools/calvincTools/mathexpr_parser/eval.py — reference evaluator API behavior
- F:/calvincTools/calvincTools/database.py — reference repository/session behavior to replicate in C++
- F:/calvincTools/calvincTools/models.py — reference schema/model mapping to migrate
- F:/calvincTools/calvincTools/usr_auth/models.py — reference authentication model behavior
- F:/calvincTools/calvincTools/usr_auth/decorators.py — reference authorization semantics to port into service checks
- F:/calvincTools/calvincTools/cMenu/menucommand_constants.py — source command taxonomy for C++ enum/registry
- F:/calvincTools/calvincTools/cMenu/cMenu.py — source behavior for Qt/C++ UI rewrite
- F:/calvincTools/calvincTools/cMenu/cEditMenu.py — source behavior for menu editor UI rewrite

**Verification**
1. Configure/build validation: clean configure and build succeeds for all C++ targets in calvincTools-cpp using CMake on Windows (and later Linux/macOS once CI is added).
2. C++ unit verification: CTest passes for each migrated module (mathexpr, database, auth, menucommand, ui) before moving to next phase.
3. Behavior parity checks: module-level C++ tests assert equivalent behavior to selected Python source cases for parser outputs, auth rules, and command dispatch routing.
4. Integration verification: end-to-end C++ app startup test validates DB init, user auth lifecycle, command execution path, and core UI navigation.
5. Regression gate per phase: no phase is marked complete until relevant C++ unit and integration tests are green.

**Decisions**
- Selected strategy: full C++ rewrite target.
- Phase 1 includes: mathexpr_parser, database/models abstraction, usr_auth non-UI logic, cMenu command system non-UI.
- UI direction: start Qt/C++ UI rewrite now.
- Compatibility: new C++ API first; Python compatibility deferred.
- Validation gate: C++ tests only for migrated modules.
- Constraint: place all newly created implementation files under calvincTools-cpp.

**Further Considerations**
1. Database stack choice recommendation: Option A use raw SQLite + lightweight repository layer for fastest delivery; Option B adopt a C++ ORM/query builder for maintainability.
2. Qt UI architecture recommendation: Option A QWidget-first for parity with current behavior; Option B QML-first for longer-term UI flexibility.
3. Packaging recommendation: Option A library + executable only in early phases; Option B immediate installer/distribution pipeline once app composition is stable.