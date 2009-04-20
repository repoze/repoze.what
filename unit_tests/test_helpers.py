# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009, Gustavo Narea <me@gustavonarea.net>.
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
Tests for the :mod:`repoze.what` helpers.

"""

from unittest import TestCase

from repoze.what.helpers.base import Helper


#{ The test suite


class TestHelper(TestCase):
    """
    Test case for the base :class:`Helper`.
    
    """
    
    def test_name_property(self):
        """The ``name`` attribute must not be implemented by default"""
        h = Helper()
        try:
            h.name
            self.fail("The .name attribute of Helper must not be implemented " \
                      "by default")
        except NotImplementedError:
            pass
    
    def test_helper_organizer_with_no_helper(self):
        """
        Helper.organize_helpers() should return an empty dictionary when no
        helper is given.
        
        """
        self.assertEqual({}, Helper.organize_helpers())
    
    def test_helper_organizer_with_unique_helpers(self):
        """
        Helper.organize_helpers() should organize unique helpers correctly.
        
        """
        h1 = MockHelper('name1')
        h2 = MockHelper('name2')
        h3 = MockHelper('name3')
        helpers_organized = {
            'name1': h1,
            'name2': h2,
            'name3': h3,
        }
        self.assertEqual(helpers_organized, Helper.organize_helpers(h1, h2, h3))
    
    def test_helper_organizer_with_duplicate_helpers(self):
        """
        Helper.organize_helpers() can't organize duplicate helpers.
        
        """
        h1 = MockHelper('name1')
        h2 = MockHelper('name1')
        h3 = MockHelper('name3')
        self.assertRaises(IndexError, Helper.organize_helpers, h1, h2, h3)


#{ Mock definitions


class MockHelper(Helper):
    """
    Mock helper for this test suite.
    
    """
    
    def __init__(self, helper_name, return_value=None):
        self.helper_name = helper_name
        self.return_value = return_value
    
    @property
    def name(self):
        return self.helper_name


#}
