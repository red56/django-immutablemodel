from setuptools import setup
import os
from distutils.core import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()

setup(
    name = 'django-immutablefield',
    version = '0.2',
    description="A base class for Django to allow immutable fields on Models",
    long_description=README + '\n\n' + NEWS,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Database'
    ],
    keywords='django model fields immutable frozen',
    author='Rob Madole',
    author_email='robmadole@gmail.com',
    url='http://bitbucket.org/robmadole/django-immutablefield',
    packages = [ 'immutablefield' ],
    zip_safe=False,
    entry_points={}
)
