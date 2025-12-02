"""
calvincTools - A Python package
"""

__version__ = "1.2.0"
__author__ = "Calvin C"
__email__ = "calvinc404@gmail.com"

_pkgname='Calvin C Tools'
_base_ver_major=1
_base_ver_minor=2
_base_ver_patch=0
_ver_date='2025-12-01'
_base_ver = f'{_base_ver_major}.{_base_ver_minor}.{_base_ver_patch}'
sysver = {
    'DEV': f'DEV{_base_ver}', 
    'PROD': _base_ver,
    'DEMO': f'DEMO{_base_ver}'
    } 

sysver_key = 'DEV'

# Change Log:
# 1.2.0 - 2025-11-30 - redesigned cEditMenu form, used internal API more, cleaned up code, added cGridWidget and other utils, added internal variable fields to cQForm classes
# 1.0.0 - 2024-11-?? - initial release
# Import main modules here as needed
# from .module import function
