# encoding: utf-8
# Django settings for temp project.

DATABASES = {
    'default': {
        'NAME': ':memory:',
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django_nose',
    'tests.testapp',
)

MIDDLEWARE_CLASSES=[]

SECRET_KEY = '-test-'

TEST_RUNNER = 'django_nose.runner.NoseTestSuiteRunner'
