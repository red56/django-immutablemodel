#! /usr/bin/env python
'''
file to run in jenkins
'''
import os
import sys

ROOT = os.path.abspath(os.path.dirname(__file__))
VIRTUALENV_DIR = os.path.join(os.path.dirname(ROOT),'virtualenv')

def print_ln(msg):
    sys.stderr.write(msg)
    sys.stderr.write("\n")

def print_header(msg):
    print_ln("="*80)
    print_ln(" " + msg)
    print_ln("="*80)
    
def ensure_virtualenv():
    if os.path.exists(os.path.join(VIRTUALENV_DIR,'bin')):
        return
    os.path
    print_header("setting up virtualenv")
    system(
        "virtualenv -p python2.5 --no-site-packages %s" % (VIRTUALENV_DIR, )
        )
    
def pip_install():
    print_header("doing pip install")
    system(
        "%s/bin/pip install -r %s/requirements.txt" % (VIRTUALENV_DIR, ROOT, )
        )

def do_test():
    print_header("doing test")
    return_code = system(
        "%s/bin/python %s/runtests.py" % (VIRTUALENV_DIR, ROOT)
        )
    if return_code:
        sys.exit("Test failure or error")

def system(cmd):
    print_ln(cmd)
    return os.system(cmd)
    

if __name__=="__main__":
    ensure_virtualenv()
    pip_install()
    do_test()