#!/usr/bin/env python
'''
To create new release we need foolow next steps:
- ./setup.py register
  Read more: http://docs.python.org/distutils/packageindex.html
- ./setup.py sdist --formats=gztar,zip
  Read more: http://docs.python.org/distutils/sourcedist.html
- ./setup.py sdist --formats=gztar,zip  upload
  Read more: http://docs.python.org/distutils/uploading.html
'''
# by default python2.5 not support 'with' statement
from __future__ import with_statement
from setuptools import setup, find_packages
import os
import sys


def fullsplit(path, result=None):
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

packages, data_files = [], []

for dir_name in [f for f in os.listdir(os.path.dirname(__file__) or '.') if os.path.isdir(f)]:
    for dirpath, dirnames, filenames in os.walk(dir_name):
        if '__init__.py' in filenames:
            packages.append('.'.join(fullsplit(dirpath)))
        elif filenames:
            data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

with open('README') as file:
    long_description = file.read()


setup(
    name = "gaeframework",
    version = "2.0.10",
    author = "Anton Danilchenko",
    author_email = "anton.danilchenko@gaeframework.com",
    description = "GAE framework is a Python web framework for use on Google App Engine",
    long_description = long_description,
    download_url = "http://code.google.com/p/gaeframework/downloads/list",
    url = "http://www.gaeframework.com",
    include_package_data = True,
    zip_safe=False,
    scripts = ['gae-manage.py'] + [os.path.join("google_appengine", os.path.basename(path))
                                   for path
                                   in os.listdir(os.path.join(os.path.dirname(__file__), 'google_appengine'))
                                   if path.endswith('.py') and not path.startswith('__')],
    packages = find_packages(),
    classifiers=['Development Status :: 4 - Beta',
                'Environment :: Web Environment',
                'Intended Audience :: Developers',
                'License :: OSI Approved :: MIT License',
                'Operating System :: OS Independent',
                'Programming Language :: Python',
                'Programming Language :: Python :: 2.6',
                'Programming Language :: Python :: 2.7',
                'Topic :: Internet :: WWW/HTTP',
                'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
                'Topic :: Internet :: WWW/HTTP :: WSGI',
                'Topic :: Software Development :: Libraries :: Application Frameworks',
                'Topic :: Software Development :: Libraries :: Python Modules',
                ]
)
