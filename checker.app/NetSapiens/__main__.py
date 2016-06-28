from __future__ import nested_scopes, absolute_import, with_statement, print_function

try:
    from future import builtins, standard_library
    standard_library.install_aliases()
except:
    print("Missing library 'future'... To install, please execute:")
    print("pip install future")

import sys, logging
from .main import NSApacheMysqlChecker as app


if __name__ == "__main__":
  @app.bootstrap
  def app(): pass

