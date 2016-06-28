from __future__ import nested_scopes, absolute_import, with_statement, print_function
from future import builtins, standard_library
standard_library.install_aliases()

import os, sys, stat, errno, traceback
import multiprocessing, time, signal
import datetime, argparse, logging, json

from time import sleep

from .web import Web
from .db import DB
from .email import Email

__DESCRIPTION__= 'NetSapiens Apache/MySQL health watchdog'
__STATUS_QUERY__ = 'SELECT Id,User,Host,Db,Command as Mode,Time,State,Info from INFORMATION_SCHEMA.PROCESSLIST order by time'
__LOG_FORMAT__ = '%(asctime)s %(module)s:%(message)s'

__ARGUMENTS__ = {
    'args': {
      'db-host': {
        'arg': ['--db-host' ] ,
        'opt': { 'help': 'MySQL Host name', 'type': str, 'action': 'store', 'default': 'localhost', 'metavar': 'hostname' }
      },
      'db-port': {
        'arg': [ '--db-port' ],
        'opt': { 'help': 'MySQL TCP Port', 'type': int, 'action': 'store', 'default': 3306, 'metavar': 'port' }
        },
      'db-user': {
        'arg': [ '--db-user' ],
        'opt': { 'help': 'MySQL Username', 'type': str, 'action': 'store', 'default': 'root', 'metavar': 'user' }
        },
      'db-pass': {
        'arg': [ '--db-pass' ],
        'opt': { 'help': 'MySQL Password', 'type': str , 'action': 'store', 'default': 'sipbx', 'metavar': 'password'}
        },
      'db-name': {
        'arg': [ '--db-name' ],
        'opt': { 'help': 'MySQL Password', 'type': str , 'action': 'store', 'default': 'SiPbxDomain', 'metavar': 'database' }
        },

      'web-url': {
        'arg': [ '--web-url' ],
        'opt': { 'help': 'URL to use as a baseline', 'type': str, 'action': 'store', 'default': 'https://localhost/server-info', 'metavar': 'Full URL' }
        },
      'web-timeout': {
        'arg': [ '--web-timeout' ],
        'opt': { 'help': 'Web connection timeout', 'type': int, 'action': 'store', 'default': 3, 'metavar': 'seconds' }
        },
      'web-ignore-cert': {
        'arg': [ '-k', '--web-ignore-cert', '-k' ],
        'opt': { 'help': 'Ignore SSL certificate trust', 'action': 'store_true', 'default': False }
        },

      'email-pretest': {
        'arg': [ '--email-pretest' ],
        'opt': { 'help': 'Send a test email prior to entering the loopty-loop', 'action': 'store_true', 'default': False }
        },
      'email-host': {
        'arg': [ '--email-host' ],
        'opt': { 'help': 'eMail relay server to leverage', 'type': str, 'default': None, 'metavar': 'hostname' }
        },
      'email-port': {
        'arg': [ '--email-port' ],
        'opt': { 'help': 'eMail relay server port', 'type': int, 'default': 25, 'metavar': 'port' }
        },
      'email-from': {
        'arg': [ '--email-from' ],
        'opt': { 'help': 'From eMail address to use', 'type': str, 'default': None }
        },
      'email-to': {
        'arg': [ '--email-to' ],
        'opt': { 'help': 'eMail to send the triggered report', 'type': str, 'default': 'tmodelli@netsapiens.com' }
        },
      'email-cc': {
        'arg': [ '--email-cc' ],
        'opt': { 'help': 'eMail address to copy the triggered report', 'type': str, 'default': None }
        },
      'email-subject': {
        'arg': [ '--email-subject' ],
        'opt': { 'help': 'eMail subject line', 'type': str, 'default': None }
        },

      'db-reconnect': {
        'arg': [ '--db-reconnect' ],
        'opt': { 'help': 'Retry timmer for database reconnection', 'action': 'store', 'type': int, 'default': 0, 'metavar': 'seconds' }
        },

      'wait-cycle': {
        'arg': [ '--wait-cycle' ],
        'opt': { 'help': 'Time to wait between sucesefull checks', 'action': 'store', 'type': int, 'default': 60, 'metavar': 'seconds' }
        },
      'debug': {
        'arg': [ '-d', '--debug' ],
        'opt': { 'help': 'enable debug', 'action': 'store_true', 'default': False }
        },
      'verbose': {
        'arg': [ '-v', '--verbose' ],
        'opt': { 'help': 'Goes into a bit more verbose mode', 'action': 'store_true', 'default': False }
        },
    }
}

class NSApacheMysqlChecker(object):
  config = None
  __db = None
  __pl = None
  __ss = None

  def __init__(self, *args, **kvp):
    try:
      self.log = logging.getLogger(__name__)
    except:
      logging.basicConfig(format=__LOG_FORMAT__, level=logging.WARNING, propagate=0)
      __log = logging.getLogger('__main__')
      self.log = logging.getLogger(__name__)


    try:
      self.args = self.__initArguments()
      self.config = self.__initConfig(args=self.args)
      self.log.debug(":%s.__init__ Initialized application sucesefully" %
              (__name__))
    except Exception as e:
      self.log.ciritcal(":%s.__init__ Failed to initialize application.\n\tArgs: %r\n\tKvp: %r\n" %
              (__name__, args, kvp))
      raise


  def __initConfig(self, args):
    __config = { }
    try:
      __config['debug'] = args.debug
      __config['quiet'] = False if args.verbose is True and args.debug is False else True
      __config['cycle'] = args.wait_cycle
    except:
      raise Exception('Minimum configuration arguments not available')
    return __config

  def __initArguments(self):
    argo = argparse.ArgumentParser(
          prog=sys.argv[0],
          prefix_chars='--',
          )

    for option in __ARGUMENTS__['args']:
      argo.add_argument(*__ARGUMENTS__['args'][option]['arg'], **__ARGUMENTS__['args'][option]['opt'])
    return argo.parse_args()

  def __sendEmail(self, err=None):
    _msg = {
      'db': self.db.lastData,
      'web': self.web.lastData,
      'err': err.message
      }
    self.email.sendMail(**_msg)
    return True

  def __loop(self):
    self.log.info(":%s.__loop Entering watch loop..." % __name__)
    __cycle = self.config['cycle']
    while True:
      try:
        self.db.fetchProcessList()
      except KeyboardInterrupt:
        raise
      except Exception as e:
        if self.db.config['reconnect'] > 0:
          __sleep = self.db.config['reconnect']
          self.log.warning(":%s.__loop Database Unavailable: Sleeping %d seconds due to db-reconnect flag" %
              (__name__, self.db.config['reconnect']))
        else:
          self.log.critical(":%s.__loop Exiting script due to database connection failure..." % (__name__))
          self.log.debug(":%s.__loop Library returned %r" % (__name__, e))
          raise
      else:
        self.log.debug(":%s.__loop Downloaded database info and stored in XXX" % (__name__))
        try:
          self.web.checkStatus()
        except KeyboardInterrupt:
          raise
        except Exception as e:
          self.log.debug(":%s.__loop Web connection failure with %r" % (__name__, e))
          self.log.error(":%s.__loop Web connectino NOT sucessefull... Flushing email out" % (__name__))
          self.__sendEmail(e.message)
          return(-1)
        else:
          __sleep = __cycle
      time.sleep(__sleep)

  def run(self):
    self.web = Web(args=self.args)
    self.db = DB(args=self.args)
    self.email = Email(args=self.args)

    try:
      self.__loop()
    except KeyboardInterrupt:
      raise
    except Exception as e:
      self.log.critical(":%s.run Unknown error occured... Existing" % (__name__))
      self.log.critical(":%s.run Library returned %r" % (__name__, e))
      raise

  @staticmethod
  def bootstrap(*args, **kvp):
    logging.basicConfig(format=__LOG_FORMAT__, level=logging.WARN, propagate=1)
    log = logging.getLogger()
    app = NSApacheMysqlChecker()

    requests_log = logging.getLogger("requests")
    requests_log.setLevel(logging.ERROR)
    requests_log.propagate = True

    if app.config['debug'] is True:
      log.setLevel(logging.DEBUG)
    elif app.config['quiet'] is True:
      log.setLevel(logging.WARN)
    else:
      log.setLevel(logging.INFO)
    log.debug(":%s.bootstrap initialized bootstrap... Looping: " % (__name__))

    try:
      app.run()
    except KeyboardInterrupt:
      log.critical("User cancled loop via CTRL+C")
      sys.exit(errno.ECANCELED)
    except Exception as e:
      if app.config['debug']:
        raise
      else:
        sys.exit(-1)

if __name__ == "__main__":
  raise SystemError
else:
   """We are being loaded as a module"""
   pass
