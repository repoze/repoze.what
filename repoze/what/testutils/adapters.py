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

"""Utilities to test source adapters."""

from repoze.what.adapters import SourceError, ExistingSectionError, \
                                         NonExistingSectionError, \
                                         ItemPresentError, ItemNotPresentError

__all__ = ['GroupsAdapterTester', 'PermissionsAdapterTester',
           'ReadOnlyGroupsAdapterTester', 'ReadOnlyPermissionsAdapterTester']


class _ReadOnlyBaseAdapterTester(object):
    """Base test case for read-only adapters"""
    
    def _get_all_items(self):
        all_items = set()
        for items in self.all_sections.values():
            all_items |= items
        return all_items
    
    def _get_item_sections(self, item):
        return set([n for (n, s) in self.all_sections.items() if item in s])
    
    def test_retrieving_all_sections(self):
        self.assertEqual(self.adapter._get_all_sections(), self.all_sections)
    
    def test_getting_section_items(self):
        for section_name, items in self.all_sections.items():
            self.assertEqual(self.adapter._get_section_items(section_name),
                             items)
    
    def test_checking_existing_section(self):
        for section_name in self.all_sections.keys():
            assert self.adapter._section_exists(section_name), \
                   'Section "%s" does NOT exist' % section_name
    
    def test_checking_non_existing_section(self):
        section_name = u'i_dont_exist'
        assert not self.adapter._section_exists(section_name), \
               'Section "%s" DOES exist' % section_name
    
    def test_checking_item_inclusion(self):
        for section_name, items in self.all_sections.items():
            for item in self.adapter._get_section_items(section_name):
                assert self.adapter._item_is_included(section_name, item), \
                       'Item "%s" must be included in section "%s"' % \
                       (item, section_name)
    
    def test_checking_excluded_item_inclusion(self):
        excluded_item = self.new_items.pop()
        for section_name, items in self.all_sections.items():
            assert not self.adapter._item_is_included(section_name,
                                                      excluded_item), \
                   'Item "%s" must not included in section "%s"' % \
                       (item, section_name)
    
    def test_checking_section_existence(self):
        for section_name in self.all_sections.keys():
            assert self.adapter._section_exists(section_name), \
                   'Section "%s" must exist' % section_name
    
    def test_checking_non_existing_section_existence(self):
        invalid_section = u'designers'
        assert not self.adapter._section_exists(invalid_section), \
                   'Section "%s" must not exist' % invalid_section

    def test_sets_if_it_is_writable(self):
        assert hasattr(self.adapter, 'is_writable'), \
               "The adapter doesn't have the 'is_writable' attribute; " \
               "please call its parent's constructor too"


class _BaseAdapterTester(_ReadOnlyBaseAdapterTester):
    """Base test case for read & write adapters"""
    
    def test_adding_many_items_to_section(self):
        for section_name, items in self.all_sections.items():
            self.adapter._include_items(section_name, self.new_items)
            final_items = items | self.new_items
            assert self.adapter._get_section_items(section_name)==final_items, \
                   '"%s" does not include %s' % (section_name, self.new_items)
    
    def test_creating_section(self):
        section = u'cool-section'
        self.adapter._create_section(section)
        assert section in self.adapter._get_all_sections().keys(), \
               'Section "%s" could not be added' % section
    
    def test_editing_section(self):
        old_section = self.all_sections.keys()[0]
        new_section = u'cool-section'
        self.adapter._edit_section(old_section, new_section)
        assert new_section in self.adapter._get_all_sections().keys() and \
               old_section not in self.adapter._get_all_sections().keys(), \
               'Section "%s" was not renamed to "%s"' % (old_section,
                                                         new_section)

    def test_deleting_section(self):
        section = self.all_sections.keys()[0]
        self.adapter._delete_section(section)
        assert section not in self.adapter._get_all_sections().keys(), \
               'Section "%s" was not deleted' % section


class ReadOnlyGroupsAdapterTester(_ReadOnlyBaseAdapterTester):
    """
    Test case for read-only groups source adapters.
    
    The groups source used for the tests must only contain the following
    groups (aka "sections") and their relevant users (aka "items"; if any):
    
    * admins
       * rms
    * developers
       * rms
       * linus
    * trolls
       * sballmer
    * python
    * php
    
    .. attribute:: adapter
    
        An instance of the :term:`group adapter` to be tested.
    
    For example, a test case for the mock group adapter
    ``FakeReadOnlyGroupSourceAdapter`` may look like this::
    
        from repoze.what.adapters.testutil import ReadOnlyGroupsAdapterTester
        
        class TestReadOnlyGroupsAdapterTester(ReadOnlyGroupsAdapterTester, 
                                              unittest.TestCase):
            def setUp(self):
                super(TestReadOnlyGroupsAdapterTester, self).setUp()
                self.adapter = FakeReadOnlyGroupSourceAdapter()
    
    .. note::
        
        :class:`GroupsAdapterTester` extends this test case to check write
        operations.
    
    """
    
    new_items = set((u'guido', u'rasmus'))
    
    def setUp(self):
        self.all_sections = {
            u'admins': set((u'rms', )),
            u'developers': set((u'rms', u'linus')),
            u'trolls': set((u'sballmer', )),
            u'python': set(),
            u'php': set()
        }
    
    def _make_credentials(self, userid):
        """
        Return a fake :mod:`repoze.what` ``credentials`` dictionary based on 
        the ``userid``.
        
        Overwrite this method if its generated ``credentials`` dictionaries 
        are not suitable for your adapter.
        
        """
        return {'repoze.what.userid': userid}
    
    def test_finding_groups_of_authenticated_user(self):
        for userid in self._get_all_items():
            credentials = self._make_credentials(userid)
            self.assertEqual(self.adapter._find_sections(credentials),
                             self._get_item_sections(userid))
    
    def test_finding_groups_of_non_existing_user(self):
        credentials = self._make_credentials(u'gustavo')
        self.assertEqual(self.adapter._find_sections(credentials), set())


class GroupsAdapterTester(ReadOnlyGroupsAdapterTester, _BaseAdapterTester):
    """
    Test case for groups source adapters.
    
    This test case extends :class:`ReadOnlyGroupsAdapterTester` to test
    write operations in read & write adapters and it should be set up the same
    way as its parent. For example, a test case for the mock group adapter
    ``FakeGroupSourceAdapter`` may look like this::
    
        from repoze.what.adapters.testutil import GroupsAdapterTester
        
        class TestGroupsAdapterTester(GroupsAdapterTester, unittest.TestCase):
            def setUp(self):
                super(TestGroupsAdapterTester, self).setUp()
                self.adapter = FakeGroupSourceAdapter()
    
    """
    
    def test_removing_many_users_from_group(self):
        group = u'developers'
        users = (u'rms', u'linus')
        self.adapter._exclude_items(group, users)
        assert self.adapter._get_section_items(group)==set(), \
               '"%s" still includes %s' % (group, users)


class ReadOnlyPermissionsAdapterTester(_ReadOnlyBaseAdapterTester):
    """
    Test case for read-only permissions source adapters.
    
    The permissions source used for the tests must only contain the following
    permissions (aka "sections") and their relevant groups (aka "items"; if
    any):
    
    * see-site
       * trolls
    * edit-site
       * admins
       * developers
    * commit
       * developers
    
    .. attribute:: adapter
    
        An instance of the :term:`permission adapter` to be tested.
    
    For example, a test case for the mock permission adapter defined above
    (``FakeReadOnlyPermissionSourceAdapter``) may look like this::
    
        from repoze.what.adapters.testutil import ReadOnlyPermissionsAdapterTester
        
        class TestReadOnlyPermissionsAdapterTester(ReadOnlyPermissionsAdapterTester,
                                                   unittest.TestCase):
            def setUp(self):
                super(TestReadOnlyPermissionsAdapterTester, self).setUp()
                self.adapter = FakeReadOnlyPermissionSourceAdapter()
    
    .. note::
        
        :class:`PermissionsAdapterTester` extends this test case to check write
        operations.
    
    """
    
    new_items = set((u'python', u'php'))
    
    def setUp(self):
        self.all_sections = {
            u'see-site': set((u'trolls', )),
            u'edit-site': set((u'admins', u'developers')),
            u'commit': set((u'developers', ))
        }
    
    def test_finding_permissions(self):
        for group in self._get_all_items():
            self.assertEqual(self.adapter._find_sections(group),
                             self._get_item_sections(group))
    
    def test_finding_permissions_of_non_existing_group(self):
        self.assertEqual(self.adapter._find_sections(u'designers'), set())


class PermissionsAdapterTester(ReadOnlyPermissionsAdapterTester,
                               _BaseAdapterTester):
    """
    Test case for permissions source adapters.
    
    This test case extends :class:`ReadOnlyPermissionsAdapterTester` to test
    write operations in read & write adapters and it should be set up the same
    way as its parent. For example, a test case for the mock group adapter
    ``FakePermissionSourceAdapter`` may look like this:
    
    For example, a test case for the mock permission adapter defined above
    (``FakePermissionSourceAdapter``) may look like this::
    
        from repoze.what.adapters.testutil import PermissionsAdapterTester
        
        class TestPermissionsAdapterTester(PermissionsAdapterTester,
                                           unittest.TestCase):
            def setUp(self):
                super(TestPermissionsAdapterTester, self).setUp()
                self.adapter = FakePermissionSourceAdapter()
    
    """
    
    def test_deying_permisssion_to_many_groups(self):
        permission = u'edit-site'
        groups = (u'admins', u'developers')
        self.adapter._exclude_items(permission, groups)
        assert self.adapter._get_section_items(permission)==set(), \
               '"%s" still includes %s' % (permission, groups)
