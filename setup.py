from setuptools import setup
import os
from distutils.core import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()

setup(
    name = 'django-immutablemodel',
    version = '0.3.3',
    description="A base class for Django to allow immutable fields on Models",
    long_description=README + '\n\n' + NEWS,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Database'
    ],
    keywords='django model fields immutable frozen',
    author='Rob Madole, Helder Silva, Tim Diggins',
    author_email='tim@red56.co.uk',
    url='https://github.com/red56/django-immutablemodel',
    packages = [ 'immutablemodel' ],
    zip_safe=False,
    entry_points={}
)
