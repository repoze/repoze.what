# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007, Agendaless Consulting and Contributors.
# Copyright (c) 2008, Florent Aide <florent.aide@gmail.com>.
# Copyright (c) 2008-2009, Gustavo Narea <me@gustavonarea.net>.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE.
#
##############################################################################

import os

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
version = open(os.path.join(here, 'VERSION.txt')).readline().rstrip()

setup(name='repoze.what',
      version=version,
      description=('Authorization framework for WSGI applications'),
      long_description=README,
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Application Frameworks"
        ],
      keywords='authorization web application server wsgi repoze',
      author="Gustavo Narea",
      author_email="repoze-dev@lists.repoze.org",
      namespace_packages = ['repoze', 'repoze.what', 'repoze.what.plugins'],
      url="http://static.repoze.org/whatdocs/",
      license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
      packages=find_packages(exclude=['tests', 'functional_tests']),
      package_data={
        '': ['VERSION.txt', 'README.txt'],
        'docs': ['Makefile', 'source/*']},
      exclude_package_data={'': ['README.txt', 'docs']},
      include_package_data=True,
      zip_safe=False,
      tests_require = [
        'repoze.who >= 1.0',
        'repoze.who-testutil >= 1.0b2',
        'Paste',
        'coverage',
        'nose',
        ],
      install_requires=[
        'repoze.who >= 1.0, <= 1.99', 
        'repoze.who-testutil >= 1.0b2', 
        'Paste > 1.7',
        ],
      test_suite="nose.collector",
      entry_points = """\
      """
      )
