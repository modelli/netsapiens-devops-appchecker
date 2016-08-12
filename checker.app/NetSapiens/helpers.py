from __future__ import nested_scopes, absolute_import, with_statement, print_function

import time, json
from collections import deque

class FILO(object):
    __f = None
    __datav = None
    __maxdata = 10
    __saveTime = False

    def __init__(self, f, *args, **kvp):
        self.__f = f
        self.__datav = deque(maxlen=self.__maxdata)

    def __get__(self, obj, objtype):
        try:
            if obj.config['debug'] == True:
                _ret = self.__datav.list()
            else:
                _ret = self.__datav.pop()
        except:
            _ret = None
        finally:
            return _ret

    def __int__(self):
        return len(self.__datav)

    def __str__(self):
        return str(*self.__datav)

    def __set__(self, obj, val):
        try:
            len(val)
        except:
            val = 'No data provided'
        _msg = json.dumps({ 'time': time.asctime(), 'data': val })
        self.__datav.append(_msg)
