from django.core.management import setup_environ

from immutablefield.tests import settings

setup_environ(settings)

from django.conf import settings
