from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()

version = '0.1'

install_requires = []

setup_requires = ['nose>=0.11.3', 'django>=1.1.1', 'py>=1.2.1', 'coverage>=3.3.1']


setup(name='django-immutablefield',
    version=version,
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
    license='BSD',
    packages=find_packages('src'),
    package_dir={'': 'src'},include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    setup_requires=setup_requires,
    entry_points={}
)
