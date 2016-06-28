#!/usr/bin/env python

from __future__ import nested_scopes, absolute_import, with_statement, print_function
#from future import builtins, standard_library

import os, sys, stat, errno, traceback, logging

import mysql.connector, json
from . import helpers


__DESCRIPTION__= 'NetSapiens Apache/MySQL health watchdog'
__STATUS_QUERY__ = 'SELECT Id,User,Host,Db,Command as Mode,Time,State,Info from INFORMATION_SCHEMA.PROCESSLIST order by time'

class DB(object):
  """Manages the MySQL database connection for status retrival"""
  statusQuery = __STATUS_QUERY__
  _raw = None
  cnx = None
  config = { }

  @helpers.FILO
  def lastData(self):
    __maxdata = 10
    __display = 1
    __debug = self.config.get('debug', False)

  def __init__(self, args=None):
    try:
      self.log = logging.getLogger(__name__)
      self.config = self.__initConfig(args)
      self.status = { } #self.__statusTuple()
      self.getPool()
      self.log.info(':%s DB service initialized for MySQL mysql://%s:******@%s:%d/%s' %
        (__name__, self.config['mysql']['user'], self.config['mysql']['host'],
          self.config['mysql']['port'], self.config['mysql']['database']))
    except Exception as e:
      raise

  def __initConfig(self, args=None):
    __config = {
        'reconnect': args.db_reconnect,
        'debug': args.debug,
        'mysql': {
          'user': args.db_user,
          'host': args.db_host,
          'port': args.db_port,
          'password': args.db_pass,
          'database': args.db_name
          }
        }
    return __config

  @classmethod
  def __updatePool(self, ldb):
    if ldb is None:
      return False

    self.cnx = ldb
    self.poolId = self.cnx.connection_id
    _vers = None
    try:
      for _ver in self.cnx.get_server_version():
        if _vers is None:
          _vers = str(_ver)
        else:
          _vers = _vers + "." + str(_ver)
    except:
      raise
    else:
      self.vers = _vers
    return True

  def getPool(self):
    _db = None

    if self.cnx is not None and self.checkConnection() is True:
      self.log.debug(':%s.getPool Using existing and valid connection' % __name__)
      return True
    elif self.cnx is not None:
      del(self.cnx)

    try:
      self.log.debug(':%s.getPool Attempting to connect to MySQL database using: %s:%d ' %
          (__name__,self.config['mysql']['host'], self.config['mysql']['port']))
      _db = mysql.connector.MySQLConnection(**self.config['mysql'])
    except KeyboardInterrupt:
      raise
    except mysql.connector.Error as e:
      self.log.error(':%s %r' %
          (__name__, e))
      raise
    except Exception as e:
      self.log.error(':%s.getPool unknown error while attempting to get a database connection %r' %
          (__name__, e))
      raise
    else:
      self.log.debug(':%s.getPool Sucesefully stabilished connection to MySQl Server' % __name__)
    return self.__updatePool(_db)


  def checkConnection(self):
    if self.cnx is None:
      return False
    try:
      self.cnx.is_connected()
    except mysql.connector.Error as e:
      self.log.debug(':%s.checkConnection connection was lost!' % __name__)
      return False
    except Exception as e:
      raise
    else:
      self.log.debug(':%s.checkConnection MySQL connection is healthy and alive!' % __name__)
      return True


  def fetchProcessList(self):
    if self.getPool() == False:
      raise

    cursor = None
    try:
      cursor = self.cnx.cursor(dictionary=True)
      cursor.execute(self.statusQuery)
      self._header = cursor.column_names
      self._raw = cursor.fetchall()
      _data = []
      for _r in self._raw:
        _data.append(_r)
    except KeyboardInterrupt:
      raise
    except Exception as e:
      self.log.debug(':%s.fetchProcessList: database connection error' % (__name__))
      if self.cnx is not None:
        self.cnx.close()
      raise
    else:
      self.lastData = _data
    finally:
      if cursor is not None:
        cursor.close()
    return True

if __name__ == "__main__":
   """We are being loaded as a program???"""
   pass

