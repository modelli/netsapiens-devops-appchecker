#!/usr/bin/env python

from __future__ import nested_scopes, absolute_import, with_statement, print_function
#from future import builtins, standard_library

import os, sys, stat, errno, traceback
import multiprocessing, time, signal
import datetime, argparse, logging, json

import platform, subprocess, email.encoders

from subprocess import PIPE
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from time import sleep

__DESCRIPTION__="NetSapiens Apache/MySQL health watchdog"

class Email(object):
  def __init__(self, args=None):
    self.log = logging.getLogger(__name__)
    self.config = self.__initConfig(args)
    self.testEmail()
    self.log.info(':%s Email services initialized sucesefully...' % (__name__))


  def __initConfig(self, args=None):
    try:
      args.email_from
      if args.email_from is None:
        raise ValueError
    except:
      args.email_from =  'checker.app@%s' % platform.node()

    __config = {
        'server': {
          'host': args.email_host,
          'port': args.email_port,
          'timeout': 3
          },
        'header': {
          'from': args.email_from,
          'to':   args.email_to,
          'cc':   args.email_cc,
          'subject': args.email_subject
          },
        'debug': args.debug,
        'pretest': args.email_pretest
        }
    try:
      if args.email_host != None: raise NotImplementedError
    except Exception as e:
      _msg = 'SMTP protocol as not been not implemented yet'
      self.log.critical(':%s.__initConfig %s' % (__name__, _msg))
      raise NotImplementedError(_msg)
    return __config


  def testEmail(self):
    if self.config['pretest'] == False:
      return True

    try:
      self.sendMail(_test=True)
      self.log.debug(':%s.testEmail Test was sucesefull...' 
          % (__name__))
    except Exception as e:
      self.log.error(':%s.testEmail Test was failed...' 
          % (__name__))
      self.log.debug(':%s.testEmail Library returned %s' 
          % (__name__, e.message))
      raise
    return True


  def __buildHeader(self, _mime, _test=False):
    if type(_mime) is None:
      raise TypeError('message must be in Mime format')
    _mime['From'] = self.config['header']['from']
    _mime['To'] = self.config['header']['to']
    _mime['Cc'] = self.config['header']['cc']
    if _test:
      _s = 'pre-flight email test for'
    else:
      _s = 'caught a failure on server'
    _mime['Subject'] = 'checker.app %s %s at %s' % (_s, platform.node(),time.asctime())
    return _mime


  def __buildBody(self, _mime, _test=None, **msg):
    _b = []
    _p = ""
    _m = None
    if _test:
      _p = "{ 'message': 'Test email for %s script' }" % __name__
    else:
      for _k in msg:
        _message = None
        try:
          _message = str(msg[_k]).strip()
        except:
          _message = "NO DATA TO DELIVER"
        else:
          if _message is None or len(_message) == 0:
            _message = "NO DATA TO DELIVER"

        try:
          if _message[:6] == "<html>":
            _t = 'html'
            _m = MIMEText(_message, _t, 'utf-8')
            _file = "%s.%s" % (_k, _t)
          elif _message[0] == '{' and _message[-1] == '}':
            _t = 'json'
            _m = MIMEText(_message, 'plain', 'utf-8')
            _file = "%s.%s" % (_k, _t)
          else:
            _t = 'plain'
            _m = MIMEText(str(_message), 'plain', 'utf-8')
            _file = "%s.%s" % (_k, 'txt')
        except Exception as e:
          self.log.debug("%s.__buildBody Error loading mime for entry %s... Data is bellow:\n%r\n%r" %
              (__name__, _k, e.message, _message))
          _m = MIMEBase('application', 'octet-stream')
          _m.set_payload(_message)
          email.encoders.encode_base64(_m)
          _file = "%s.%s" % (_k, 'bin')
        _m.add_header('Content-Disposition', 'attachment', filename=_file)
        _mime.attach(_m)
      if _m == None:
        _p = "{ 'message': 'No data to deliver' }"
      else:
        _p = "{ 'message': 'Web, DB and Error messages attached' }"
    _mime.preamble = _p



  #XXX: This function could use a lot of work utilizing MIMEs and attachmenets
  def sendMail(self, _test=False, **msg):
    _mime = MIMEMultipart()
    self.__buildHeader(_mime, _test)
    self.__buildBody(_mime, _test, **msg)

    if self.config['debug'] is True and self.config['pretest'] is False:
      sendmail_location = ['/usr/sbin/sendmail', '-t', '-oi'] # sendmail location
      #sendmail_location = ['/bin/sh', '-c', 'cat>/dev/stderr']
    else:
      sendmail_location = ['/usr/sbin/sendmail', '-t', '-oi'] # sendmail location
    #self.log.debug(':%s.sendMail : Attempting to send email using local sendmail at %r' %
    #      (__name__, sendmail_location))
    try:
      p = subprocess.Popen(args=sendmail_location, stdin=PIPE)
      p.communicate(_mime.as_string())
      _status = p.pipe_cloexec()
    except Exception as e:
      self.log.critical(':%s.sendMail Failed to send email...' % (__name__))
      self.log.debug(':%s.sendMail Library returned %r' % (__name__, e))
      raise
    else:
      self.log.info(':%s.sendMail EMail sent sucesefully' %
          (__name__))
    return True

if __name__ == "__main__":
   """We are being loaded as a program???"""
   pass

