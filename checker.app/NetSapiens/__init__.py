from __future__ import nested_scopes, absolute_import, with_statement, print_function

try:
    from future import builtins, standard_library
    standard_library.install_aliases()
except:
    print("Missing library 'future'... To install, please execute:")
    print("pip install future")

from .main import NSApacheMysqlChecker
