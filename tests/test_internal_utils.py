# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009-2010, Gustavo Narea <me@gustavonarea.net>.
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
Tests for the internal utilities at :mod:`repoze.what._utils`.

"""

from nose.tools import eq_

from repoze.what._utils import normalize_path


class TestNormalizingPath(object):
    """Tests for :func:`normalize_path`."""
    
    def test_empty_string(self):
        path_normalized = normalize_path("")
        eq_(path_normalized, "/")
    
    def test_slash(self):
        path_normalized = normalize_path("/")
        eq_(path_normalized, "/")
    
    def test_no_leading_slash(self):
        path_normalized = normalize_path("path/")
        eq_(path_normalized, "/path/")
    
    def test_no_trailing_slash(self):
        path_normalized = normalize_path("/path")
        eq_(path_normalized, "/path/")
    
    def test_trailing_and_leading_slashes(self):
        path_normalized = normalize_path("/path/")
        eq_(path_normalized, "/path/")
    
    def test_multiple_leading_slashes(self):
        path_normalized = normalize_path("////path/")
        eq_(path_normalized, "/path/")
    
    def test_multiple_trailing_slashes(self):
        path_normalized = normalize_path("/path////")
        eq_(path_normalized, "/path/")
    
    def test_multiple_inner_slashes(self):
        path_normalized = normalize_path("/path////here/")
        eq_(path_normalized, "/path/here/")
    
    def test_unicode_path(self):
        path_normalized = normalize_path(u"mañana/aquí")
        eq_(path_normalized, u"/mañana/aquí/")

