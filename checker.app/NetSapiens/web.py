#!/usr/bin/env python

from __future__ import nested_scopes, absolute_import, with_statement, print_function

import os, sys, stat, errno, traceback, logging

import requests
from time import sleep

from . import helpers

__DESCRIPTION__="NetSapiens Apache/MySQL health watchdog"
class Web(object):
  """Web-server status checker"""
  error = {
      'code': 0,
      'message': None
      }
  config = { }

  @helpers.FILO
  def lastData(self):
    __maxdata = 10
    __display = 1
    __saveTime = True

  def __init__(self, args=None):
    try:
      self.log = logging.getLogger(__name__)
      self.config = self.__initConfig(args)
      self.testServer()

    except Exception as e:
      self.log.critical(':%s.__init__ Web Services Initialized failed.' %
          (__name__))
      self.log.debug(':%s.__init__ Library returned %r.' %
          (__name__, e))
      sys.exit(-1)
    else:
      self.log.info(':%s Web Services Initialized sucesefully for %s' %
          (__name__, self.config['http']['url']))

  def __initConfig(self, args=None):
    __config = { }
    try:
      __config['http'] = { }
      __config['http']['url'] = args.web_url
      __config['http']['verify'] = bool(args.web_ignore_cert == False)
      __config['http']['timeout'] = args.web_timeout
      __config['http']['stream'] = False
      __config['debug'] = args.debug

    except Exception as e:
      self.log.critical('%s.__initConfig Failed to configure module. Required arguments missing')
      raise Exception(e.message)
    return __config

  def __updateError(self, args=None):
    if args == None or args.code == 200:
      return True
    self.error['code'] = code
    self.error['message'] = message
    return False

  def testServer(self): return self.checkStatus(_testServer=__name__)

  def checkStatus(self, _testServer=None):
    if _testServer is None:
      __myName = "%s.checkStatus" % __name__
    else:
      __myName = "%s.testServer" % _testServer

    try:
      self.log.debug(":%s Attempting to connect to %r" % ( __myName, self.config))
      _http = requests.get(**self.config['http'])
    except Exception as e:
      self.log.error(':%s Failed to connect to %s' %
          (__myName, self.config['http']['url']))
      self.log.debug(':%s Web library returned: %r' %
          (__myName, e.message))
      raise
    else:
      self.lastData = _http.content
      _http.close()
      self.log.debug(':%s Web connection to %s was sucesefull with response code %d (\'%s\')' %
          (__myName, self.config['http']['url'], _http.status_code, _http.reason))
    return True


