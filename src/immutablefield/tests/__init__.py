# encoding: utf-8
from django.core.management import setup_environ, call_command

from immutablefield.tests import settings

setup_environ(settings)
call_command('syncdb', interactive=False) 
