#!/usr/bin/env python

from setuptools import setup

setup(name='xdocreport_restclient',
      version='0.1',
      description='Client for xdocreport REST services',
      author='Silvio Tomatis',
      author_email='silvio@gropen.net',
      url='http://github.com/silviot/xdocreport_restclient',
      packages=['xdocreport_restclient'],
      install_requires=[
        'requests'
      ]
     )
