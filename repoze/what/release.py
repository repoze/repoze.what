# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008-2009, Gustavo Narea <me@gustavonarea.net>
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

"""
repoze.what release information.

The version number is loaded to help the Quickstart plugin configure
repoze.what correctly, depending on the version available -- although it may
be useful on other packages.

"""

import os

_here = os.path.abspath(os.path.dirname(__file__))
_root = os.path.dirname(os.path.dirname(_here))

version = open(os.path.join(_root, 'VERSION.txt')).readline().rstrip()

# The major version: If version=='3.0.2rc4', the major version is int(3).
major_version = int(version.split('.')[0])
