#!/usr/bin/env python

from __future__ import nested_scopes, absolute_import, with_statement, print_function
import os
import sys
import tempfile

if sys.hexversion < 0x03040000 and sys.hexversion < 0x02070900:
    raise RuntimeError('This script requires Python2 version >= 2.7.9 or Python3 version >= 3.4')

if hasattr(sys, 'real_prefix'):
   raise RuntimeError('You started this script from an already instanciated virtualenv stanza')
else:
    try:
        import pip
    except Exception as e:
        print("""
              - Error loading 'pip'. Something is wrong with this Python installation
              - Please try to update this python install by executing:
              apt-get update && apt-get install python

              - If that does not work, you can try to install pip thought debian packages via:
              apt-get update && apt-get install python-pip

              - or manually by executing the following command:
              curl https://bootstrap.pypa.io/get-pip.py | sudo sh -c "python -- && sudo python -m pip install -U pip
              """)
        raise e

try:
    import virtualenv
except Exception as e:
    print("""
          - Error instanciating the virutal enviroment. This is a catastrophic failure...
          - Something is really wrong with this Python installation

          - You could try to manually install virtualenv via:
          sudo python -m pip install -U virtualenv
          """)
    raise e

def bootstrap(folder):
    print("+- Loading pip:", end='')
    try:
        from pip.req import InstallRequirement
    except:
        print(" failed....")
        raise
    print(" done")

    try:
        print("+- Creating virtual enviroment: ", end='')
        virtualenv.create_environment(folder, site_packages=True, clear=False)
        print(" %s" % folder)
    except Exception as e:
        print(""" failed....
                - Error instanciating the virutal enviroment. This is a catastrophic failure...
                - Something is really wrong with this Python installation

                - You could try to manually install virtualenv via:
                sudo python -m pip install -U virtualenv
                """)
        raise
    else:
        return
    finally:
        pass
        #destroy_enviroment(tmpdir)


def get_dependencies():
    __DEFAULT_MODULES = ['virtualenv', 'future', 'gitpython', 'mysql_connector', 'requests' ]
    _modules = { }
    try:
        print("+- Loading dependencies file:", end='')
        _fp = open('requirements.txt', 'r')
        for line in _fp.xreadlines().strip():
           _modules.append(line)
        _fp.close()
    except:
        _modules = __DEFAULT_MODULES
    finally:
        print(" %r" % _modules)
        return _modules


def modules_install():
    _modules = get_dependencies()
    import pip
    from pip.req import InstallRequirement

    for _module in _modules:
        print("+-- Fetching and installing %s: " % (_module), end='')
        try:
           _p = pip.main(['install', '-I', '-q' , '--prefix', sys.prefix, _module])
           print(" Done!")
        except:
           print(" Failed..." )
           raise

def main_module_install():
   import git
   git.Git().clone("https://github.com/modelli/netsapiens-devops.git", 'checker.app')

   print("""
   -- Module auto-download is currently unlavailable.
   --- To download this module, please execute:
   curl -k "https://github.com/modelli/netsapiens/checker.app.tgz" | tar -zvcf -C .

   --- Once done, you should enable this virtual enviroment and run the scirpt. Next step will be to activate the
   ---- virtual enviroment created by this install script. To do so, you need to type:
   source ~/.checker.app/bin/activate

   --- Running the script
   ---- To look into the new scripts help screen, you should type:
   python -m NetSapiens --help

   ---- To run this script with the default options, which includes: Test DB and Webserver before entering the loop,
   ---- connect to the database server LOCALHOST and Web url https://localhost/server-status, and send the process to background,
   ---- you should type:
   python -m NetSapiens &

   ---- If you want to change the default url ti google and default the db host to 127.0.0.1 you should type:
   python -m NetSapiens --web-url https://google.com --db-host 127.0.0.1

   **** To use all defaults and run this script in a single line, you should type:
   curl -k "https://www.modelli.us/netsapiens/checker.app.tgz" | tar -zvcf -C . && source .checker.app/bin/activate && python -m NetSapiens &
   """)
   #_http.conf.set(dict())
   #_http.conf.update({'url': __MODULE_URL, 'verify': True, 'timeout': 6})
   #_http.web = _requests.get(**_http.conf)
   #print(_http)

print("| NetSapiens checker.app self installer...")
print("|")
try:
   print("+ Enviroment preparation...")
   _dir = '.checker.app'
   bootstrap(_dir)
   __file__ = os.path.abspath(_dir + '/bin/activate_this.py')
   print("+- Loading virtualenv @ %s:" % (__file__), end='')
   _exe = execfile(__file__, dict(__file__=__file__))
except Exception as e:
   print("-- Bootstrapping failed... %s" % e.message)
   raise
else:
   print(' done')

print("|")
try:
   print("+ Dependencies handlining...")
   modules_install()
except Exception as e:
   print("--Automated module installation failed... %s" % e.message)
   raise

print("|")
try:
   print("+ Main module installation phase...")
   main_module_install()
except Exception as e:
   print("-- Self installed failed... %s" % e.message)
   raise



