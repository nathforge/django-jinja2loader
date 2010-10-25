#!/usr/bin/env python

from distutils.core import setup

setup(
    version='0.1.1',
    url='http://github.com/nathforge/django-jinja2loader',
    name='django-jinja2loader',
    description='Jinja2 template loader for Django 1.2 and above.',
    author='Nathan Reynolds',
    author_email='nath@nreynolds.co.uk',
    packages=['jinja2loader'],
    package_dir={'': 'src'},
)

