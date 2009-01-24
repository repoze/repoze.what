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

"""Tests for the base source adapters."""

import unittest

from zope.interface import implements

from repoze.what.adapters import *

from base import FakeGroupSourceAdapter


class TestBaseSourceAdapter(unittest.TestCase):
    """
    Tests for the base source adapter.
    
    The most important thing to be checked is that it deals with its internal
    cache correctly.
    
    """
    
    def setUp(self):
        self.adapter = FakeGroupSourceAdapter()
        
    def test_cache_is_empty_initially(self):
        """No section has been loaded; the cache is clear"""
        self.assertEqual(self.adapter.loaded_sections, {})
        self.assertEqual(self.adapter.all_sections_loaded, False)
        
    def test_items_are_returned_as_sets(self):
        """The items of a section must always be returned as a Python set"""
        # Bulk fetch:
        for section in self.adapter.get_all_sections():
            assert isinstance(self.adapter.get_section_items(section), set)
    
    def test_retrieving_all_sections(self):
        self.assertEqual(self.adapter.get_all_sections(),
                         self.adapter.fake_sections)
        # Sections are in the cache now
        self.assertEqual(self.adapter.loaded_sections,
                         self.adapter.fake_sections)
        self.assertEqual(self.adapter.all_sections_loaded, True)
    
    def test_getting_section_items(self):
        self.assertEqual(self.adapter.get_section_items(u'trolls'), 
                         self.adapter.fake_sections[u'trolls'])
    
    def test_getting_items_of_non_existing_section(self):
        self.assertRaises(NonExistingSectionError, 
                          self.adapter.get_section_items,
                          'non-existing')
    
    def test_setting_section_items(self):
        items = (u'guido', u'rasmus')
        self.adapter.set_section_items(u'trolls', items)
        self.assertEqual(self.adapter.fake_sections[u'trolls'], set(items))
    
    def test_cache_is_updated_after_setting_section_items(self):
        # Loading for the first time:
        self.adapter.get_section_items(u'developers')
        # Adding items...
        items = (u'linus', u'rms')
        self.adapter.set_section_items(u'developers', items)
        # Checking the cache:
        self.assertEqual(self.adapter.get_section_items(u'developers'),
                         set(items))
    
    def test_getting_sections_by_criteria(self):
        credentials = {'repoze.what.userid': u'sballmer'}
        sections = set([u'trolls'])
        self.assertEqual(self.adapter.find_sections(credentials), sections)
    
    def test_adding_one_item_to_section(self):
        self.adapter.include_item(u'developers', u'rasmus')
        self.assertEqual(self.adapter.fake_sections[u'developers'], 
                         set((u'linus', u'rasmus', u'rms')))
    
    def test_adding_many_items_to_section(self):
        self.adapter.include_items(u'developers', (u'sballmer', u'guido'))
        self.assertEqual(self.adapter.fake_sections[u'developers'], 
                         set((u'rms', u'sballmer', u'linus', u'guido')))
    
    def test_cache_is_updated_after_adding_item(self):
        # Loading for the first time:
        self.adapter.get_section_items(u'developers')
        # Now let's add the item:
        self.adapter.include_item(u'developers', u'guido')
        self.assertEqual(self.adapter.fake_sections[u'developers'], 
                         set((u'linus', u'guido', u'rms')))
        # Now checking that the cache was updated:
        self.assertEqual(self.adapter.fake_sections[u'developers'], 
                         self.adapter.get_section_items(u'developers'))
    
    def test_removing_one_item_from_section(self):
        self.adapter.exclude_item(u'developers', u'linus')
        self.assertEqual(self.adapter.fake_sections[u'developers'], 
                         set([u'rms']))
    
    def test_removing_many_items_from_section(self):
        self.adapter.exclude_items(u'developers', (u'linus', u'rms'))
        self.assertEqual(self.adapter.fake_sections[u'developers'], set())
    
    def test_cache_is_updated_after_removing_item(self):
        # Loading for the first time:
        self.adapter.get_section_items(u'developers')
        # Now let's remove the item:
        self.adapter.exclude_item(u'developers', u'rms')
        self.assertEqual(self.adapter.fake_sections[u'developers'], 
                         set([u'linus']))
        # Now checking that the cache was updated:
        self.assertEqual(self.adapter.fake_sections[u'developers'], 
                         self.adapter.get_section_items(u'developers'))

    def test_creating_section(self):
        self.adapter.create_section('sysadmins')
        self.assertTrue('sysadmins' in self.adapter.fake_sections)
        self.assertEqual(self.adapter.fake_sections['sysadmins'],
                         set())
    
    def test_creating_existing_section(self):
        self.assertRaises(ExistingSectionError, self.adapter.create_section,
                          'developers')
    
    def test_cache_is_updated_after_creating_section(self):
        self.adapter.create_section('sysadmins')
        self.assertEqual(self.adapter.get_section_items('sysadmins'), set())
    
    def test_editing_section(self):
        items = self.adapter.fake_sections['developers']
        self.adapter.edit_section(u'developers', u'designers')
        self.assertEqual(self.adapter.fake_sections[u'designers'], items)
    
    def test_editing_non_existing_section(self):
        self.assertRaises(NonExistingSectionError, self.adapter.edit_section,
                          u'this_section_doesnt_exit', u'new_name')
    
    def test_cache_is_updated_after_editing_section(self):
        # Loading for the first time:
        self.adapter.get_section_items('developers')
        # Editing:
        description = u'Those who write in weird languages'
        items = self.adapter.fake_sections[u'developers']
        self.adapter.edit_section(u'developers', u'coders')
        # Checking cache:
        self.assertEqual(self.adapter.get_section_items(u'coders'), items)
    
    def test_deleting_section(self):
        self.adapter.delete_section(u'developers')
        self.assertRaises(NonExistingSectionError,
                          self.adapter.get_section_items, u'designers')
    
    def test_deleting_non_existing_section(self):
        self.assertRaises(NonExistingSectionError, self.adapter.delete_section,
                          u'this_section_doesnt_exit')
    
    def test_cache_is_updated_after_deleting_section(self):
        # Loading for the first time:
        self.adapter.get_section_items(u'developers')
        # Deleting:
        self.adapter.delete_section(u'developers')
        # Checking cache:
        self.assertRaises(NonExistingSectionError,
                          self.adapter.get_section_items,
                          u'developers')
    
    def test_checking_section_existence(self):
        # Existing section:
        self.adapter._check_section_existence(u'developers')
        # Non-existing section:
        self.assertRaises(NonExistingSectionError,
                          self.adapter._check_section_existence, u'designers')
    
    def test_checking_section_not_existence(self):
        # Non-existing section:
        self.adapter._check_section_not_existence(u'designers')
        # Existing section:
        self.assertRaises(ExistingSectionError,
                          self.adapter._check_section_not_existence, u'admins')
    
    def test_checking_item_inclusion(self):
        self.adapter._confirm_item_is_present(u'developers', u'linus')
        self.assertRaises(ItemNotPresentError,
                          self.adapter._confirm_item_is_present, u'developers', 
                          u'maribel')
    
    def test_checking_item_inclusion_in_non_existing_section(self):
        self.assertRaises(NonExistingSectionError,
                          self.adapter._confirm_item_is_present, u'users', 
                          u'linus')
    
    def test_checking_item_exclusion(self):
        self.adapter._confirm_item_not_present(u'developers', u'maribel')
        self.assertRaises(ItemPresentError,
                          self.adapter._confirm_item_not_present, 
                          u'developers', u'linus')
    
    def test_checking_item_exclusion_in_non_existing_section(self):
        self.assertRaises(NonExistingSectionError,
                          self.adapter._confirm_item_is_present, u'users', 
                          u'linus')


class TestBaseSourceAdapterAbstract(unittest.TestCase):
    """
    Tests for the base source adapter's abstract methods.
    
    """
    
    def setUp(self):
        self.adapter = BaseSourceAdapter()
        
    def test_get_all_sections(self):
        self.assertRaises(NotImplementedError, self.adapter._get_all_sections)
        
    def test_get_section_items(self):
        self.assertRaises(NotImplementedError, self.adapter._get_section_items,
                          None)
        
    def test_find_sections(self):
        self.assertRaises(NotImplementedError, self.adapter._find_sections,
                          None)
        
    def test_include_items(self):
        self.assertRaises(NotImplementedError, self.adapter._include_items,
                          None, None)
        
    def test_exclude_items(self):
        self.assertRaises(NotImplementedError, self.adapter._exclude_items,
                          None, None)
        
    def test_item_is_included(self):
        self.assertRaises(NotImplementedError, self.adapter._item_is_included,
                          None, None)
        
    def test_create_section(self):
        self.assertRaises(NotImplementedError, self.adapter._create_section,
                          None)
        
    def test_edit_section(self):
        self.assertRaises(NotImplementedError, self.adapter._edit_section,
                          None, None)
        
    def test_delete_section(self):
        self.assertRaises(NotImplementedError, self.adapter._delete_section,
                          None)
        
    def test_section_exists(self):
        self.assertRaises(NotImplementedError, self.adapter._section_exists,
                          None)
    
    def test_adapter_is_writable_by_default(self):
        self.assert_(self.adapter.is_writable)


class TestNotWritableSourceAdapter(unittest.TestCase):
    """Tests for an adapter dealing with a read-only source"""
    
    def setUp(self):
        self.adapter = FakeGroupSourceAdapter(writable=False)
        
    def test_setting_items(self):
        self.assertRaises(SourceError, 
                          self.adapter.set_section_items,
                          u'admins', ['gnu', 'tux'])
        
    def test_settings_items_in_non_existing_section(self):
        """The section existence must be checked first"""
        self.assertRaises(NonExistingSectionError, 
                          self.adapter.set_section_items,
                          u'mascots', ['gnu', 'tux'])
        
    def test_include_items(self):
        self.assertRaises(SourceError, self.adapter.include_item,
                          u'admins', 'tux')
        self.assertRaises(SourceError, self.adapter.include_items,
                          u'admins', ['gnu', 'tux'])
        
    def test_include_items_in_non_existing_section(self):
        """The section existence must be checked first"""
        self.assertRaises(NonExistingSectionError, self.adapter.include_item,
                          u'mascots', 'gnu')
        self.assertRaises(NonExistingSectionError, self.adapter.include_items,
                          u'mascots', ['gnu', 'tux'])
        
    def test_include_existing_items(self):
        """The items existence must be checked first"""
        self.assertRaises(ItemPresentError, self.adapter.include_item,
                          u'developers', 'rms')
        self.assertRaises(ItemPresentError, self.adapter.include_items,
                          u'developers', ['rms', 'linus'])
        
    def test_exclude_items(self):
        self.assertRaises(SourceError, self.adapter.exclude_item,
                          u'admins', u'rms')
        self.assertRaises(SourceError, self.adapter.exclude_items,
                          u'developers', [u'rms', u'linus'])
        
    def test_exclude_items_in_non_existing_section(self):
        """The section existence must be checked first"""
        self.assertRaises(NonExistingSectionError, self.adapter.exclude_item,
                          u'mascots', 'gnu')
        self.assertRaises(NonExistingSectionError, self.adapter.exclude_items,
                          u'mascots', ['gnu', 'tux'])
        
    def test_exclude_existing_items(self):
        """The items existence must be checked first"""
        self.assertRaises(ItemNotPresentError, self.adapter.exclude_item,
                          u'developers', 'rasmus')
        self.assertRaises(ItemNotPresentError, self.adapter.exclude_items,
                          u'developers', ['guido', 'rasmus'])
        
    def test_create_section(self):
        self.assertRaises(SourceError, self.adapter.create_section,
                          u'mascots')
        
    def test_create_existing_section(self):
        """The section existence must be checked first"""
        self.assertRaises(ExistingSectionError, self.adapter.create_section,
                          u'admins')
        
    def test_edit_section(self):
        self.assertRaises(SourceError, self.adapter.edit_section,
                          u'admins', u'administrators')
        
    def test_edit_non_existing_section(self):
        """The section existence must be checked first"""
        self.assertRaises(NonExistingSectionError, self.adapter.edit_section,
                          u'mascots', u'animals')
        
    def test_delete_section(self):
        self.assertRaises(SourceError, self.adapter.delete_section,
                          u'admins')
        
    def test_delete_non_existing_section(self):
        """The section existence must be checked first"""
        self.assertRaises(NonExistingSectionError, self.adapter.delete_section,
                          u'mascots')
    
    def test_adapter_is_not_writable(self):
        self.assertFalse(self.adapter.is_writable)
