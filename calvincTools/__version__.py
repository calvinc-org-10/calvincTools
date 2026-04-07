"""
calvincTools - A Python package
"""

_pkgname='Calvin C Tools'
_base_ver_major=2
_base_ver_minor=0
_base_ver_patch='0'
_ver_date='2026-04-02'
_base_ver = f'{_base_ver_major}.{_base_ver_minor}.{_base_ver_patch}'
# __version__ = _base_ver
__version__ = "2026.04.07.1130"         # Use date-based versioning for easier tracking of updates. When package stabilizes, can switch to semantic versioning if desired. Format: YYYY.MM.DD.HHMM
sysver = {
    'DEV': f'DEV{_base_ver}', 
    'PROD': _base_ver,
    'DEMO': f'DEMO{_base_ver}'
    } 

sysver_key = 'DEV'

__author__ = "Calvin C"
__email__ = "calvinc404@gmail.com"

# Change Log:
# 2.0.0 - 2026-04-02 - rewrite of cQdbRecordForm classes, notably introducing and using
#               cFormFieldDefs and cFormLayouts to replace dicts. Also restructured Form Class
#               methods extensively
# 1.8.3 - 2026-03-19 - bug fixes and code cleanup. Hopefully, conditions are passed properly now in cQdbSimpleRecordSubFormWidgets and cSimpleMultiRecordSubFmWrapperForm. Other minor bug fixes and code cleanup.
# 1.8.2 - 2026-03-19 - bug fixes
# 1.8.1 - 2026-03-19 - fixed issue in cQdbSimpleRecordSubFormWidgets where loadFromRecord was not accepting optional caller_conditions, 
#       - loadRecords methods added to handle loading with caller_conditions without parent record; 
#       - cSimpleMultiRecordSubFmWrapperForm: upon loading subform, call loadRecords if possible
#       - other minor bug fixes and code cleanup
# 1.8.0 - 2026-03-17 - split cQdbFormWidgets into separate files for better organization; other minor bug fixes and code cleanup
#       - introduce cSimpleMultiRecordSubFmWrapperForm to handle multiple record subforms with no parent record;
# 1.7.0 - 2026-03-14 
#       - cSimpleRecordSubForm1 and cSimpleRecordForm2 - parent record not required anymore, but will be used if provided; 
#       - added optional caller_conditions to loadFromRecord to allow for more flexible loading of subrecords; 
#       - other minor bug fixes and code cleanup
# 1.6.3 - 2026-01-11 - require python 3.10+; fixed code so pytest finally passes
# 1.6.2 - 2026-01-11 - modifications made to calvincTools/utils/misctools.py and corresponding tests
# 1.6.1c - 2026-01-11 - corrected linkFld getters/setters in cQdbFormWidgets.py
# 1.6.1b - 2026-01-11 - fixed issue in cQdbFormWidgets.py where parent_linkFld was not being set properly in __init__
# 1.6.1a - 2026-01-11 - bug fixes and better use of getters/setters in cQdbFormWidgets.py
# 1.6.1 - 2026-01-11 - fixed parent_linkFld property in cQdbFormWidgets.py to return actual PK value if parentRec is set
# 1.6.0 - 2026-01-10 - 
#       added is_hashable function to misctools.py
#       updated str2 function in utils/strings.py to use is_hashable from misctools, and other checks
#       modified _handleActionButton to use dictionary instead of multiple if-elif statements
#       cSimpleRecordSubForm1 and cSimpleRecordForm2 
#               - parentFK renamed linkFld, parentRecPK renamed parent_linkFld
#               - parent_linkFld doesn't have to be PK anymore, but will be if not specified
# 1.5.2 - 2026-01-06 - simplified str2 function in utils/strings.py for now - doesn't work as intended
# 1.5.1 - 2026-01-05 - fixed setup.py and pyproject.toml so that tests actually run (sort of)
#       removed calvindate tests
#       allow str2 to accept Any type
# 1.5.0 - 2026-01-04 - DeprecationWarning on calvindate class. Removal coming soon
# 1.4.0 - 2025-12-28 - added cPrintManager to utils/print.py
# 1.3.1 - 2025-12-26 - fixed issue in cFileDialogDropWidget
# 1.3.0 - 2025-12-20 - added cFileDialogDropWidget to utils/fileDialogs.py.
        # testing skipped for now
        # TODO: review and restore tests
# 1.2.4 - 2025-12-15 - bug fix - replace .kw['bind'] with .get_bind()
# 1.2.3 - 2025-12-14 - cTools_apphooks
# 1.2.2 - 2025-12-03 - fixed some bugs, pass app_sessionmaker where needed
        # DONE - v 1.2.3: set cMenu vars via subclassing - use cSimpleRecordForm as example
# 1.2.1 - 2025-12-02 - fixed import issues in menucommand_handlers.py, cMenu.py, etc
# 1.2.0 - 2025-11-30 - redesigned cEditMenu form, used internal API more, cleaned up code, added cGridWidget and other utils, added internal variable fields to cQForm classes
# 1.0.0 - 2024-11-?? - initial release
