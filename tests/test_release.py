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
Tests for the "release" module.

"""

import unittest, os

from repoze.what import release

_here = os.path.abspath(os.path.dirname(__file__))
_root = os.path.dirname(_here)
version = open(os.path.join(_root, 'VERSION.txt')).readline().rstrip()

class TestRelease(unittest.TestCase):
    def test_version(self):
        self.assertEqual(version, release.version)
    
    def test_major_version(self):
        # I prefer to update this on every major release -- Gustavo
        self.assertEqual(1, release.major_version)
