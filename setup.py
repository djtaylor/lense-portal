#!/usr/bin/python
import lense.portal as lense_portal
from setuptools import setup, find_packages

# Module version / long description
version = lense_portal.__version__
long_desc = open('DESCRIPTION.rst').read()

# Run the setup
setup(
    name='lense-portal',
    version=version,
    description='Lense API platform web portal libraries',
    long_description=long_desc,
    author='David Taylor',
    author_email='djtaylor13@gmail.com',
    url='http://github.com/djtaylor/lense-portal',
    license='GPLv3',
    packages=find_packages(),
    keywords='lense api server platform portal web ui interface',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Framework :: Django',
        'Framework :: Django :: 1.8'
    ],
    install_requires = [
        'Django>=1.8.3',
        'lense-common>=0.1',
        'lense-client>=0.1'
    ]
)