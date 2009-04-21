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

from repoze.what.helpers.base import Helper, HelperCollection


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


class TestHelperCollection(TestCase):
    """
    Test case for the :class:`HelperCollection`.
    
    """
    
    def test_without_helpers(self):
        """
        A helper collection must be an empty dictionary when no helper is given.
        
        """
        self.assertEqual({}, HelperCollection())
    
    def test_with_unique_helpers(self):
        """
        Unique helpers are organized correctly.
        
        """
        h1 = MockHelper('name1')
        h2 = MockHelper('name2')
        h3 = MockHelper('name3')
        helpers_organized = {
            'name1': h1,
            'name2': h2,
            'name3': h3,
        }
        self.assertEqual(helpers_organized, HelperCollection(h1, h2, h3))
    
    def test_with_duplicate_helpers(self):
        """
        Duplicate helpers can't be organized.
        
        """
        h1 = MockHelper('name1')
        h2 = MockHelper('name1')
        h3 = MockHelper('name3')
        self.assertRaises(IndexError, HelperCollection, h1, h2, h3)
    
    def test_getting_existing_helper(self):
        h = MockHelper('something')
        collection = HelperCollection(h)
        assert 'something' in collection
        self.assertEqual(h, collection['something'])
        self.assertEqual({'something': h}, collection)
    
    def test_getting_non_existing_helper(self):
        collection = HelperCollection(MockHelper('something'))
        assert 'anything' not in collection
        try:
            collection['anything']
            self.fail('Helper "anything" is not supposed to exist')
        except KeyError:
            pass


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
