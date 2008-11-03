# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007, Agendaless Consulting and Contributors.
# Copyright (c) 2008, Florent Aide <florent.aide@gmail.com> and
#                     Gustavo Narea <me@gustavonarea.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################

"""
Tests for the tgext.authorization middleware.

"""

import unittest

from zope.interface.verify import verifyClass
from repoze.who.interfaces import IAuthenticator, IMetadataProvider

from tgext.authorization.middleware import AuthorizationMetadata


#{ Fake adapters/plugins


class FakeGroupFetcher1(object):
    def find_sections(self, identity):
        return ('directors', 'sysadmins')


class FakeGroupFetcher2(object):
    def find_sections(self, identity):
        return ('webdesigners', 'directors')


class FakeGroupFetcher3(object):
    def find_sections(self, identity):
        return ('graphic-designers', 'sysadmins')


class FakePermissionFetcher1(object):
    def find_sections(self, group):
        if group == 'sysadmins':
            return ('view-users', 'edit-users', 'add-users')
        else:
            return ('view-users', )


class FakePermissionFetcher2(object):
    def find_sections(self, group):
        if group == 'graphic-designers':
            return ('upload-images', )
        elif group == 'directors':
            return ('hire', 'fire')
        else:
            return tuple()


class FakePermissionFetcher3(object):
    def find_sections(self, group):
        return ('contact', )


#{ The tests themselves


class TestAuthorizationMetadataBase(unittest.TestCase):
    """Tests for the L{AuthorizationMetadata} IMetadata plugin.
    
    All of these tests, except the first one, check the behavior of the plugin
    with random groups and permission fetchers.
    
    """
    
    def _check_groups_and_permissions(self, plugin, expected_groups,
                                      expected_permissions):
        identity = {'repoze.who.userid': 'whatever'}
        plugin.add_metadata(dict(), identity)
        # Using sets to forget about order:
        self.assertEqual(set(identity['groups']), set(expected_groups))
        self.assertEqual(set(identity['permissions']),
                         set(expected_permissions))

    def test_implements(self):
        verifyClass(IMetadataProvider, AuthorizationMetadata, tentative=True)
    
    def test_add_metadata1(self):
        group_fetchers = {
            'tech-team': FakeGroupFetcher1(),
            'executive': FakeGroupFetcher3()
            }
        permission_fetchers = {'perms1': FakePermissionFetcher2()}
        plugin = AuthorizationMetadata(group_fetchers, permission_fetchers)
        expected_groups = ('directors', 'sysadmins', 'graphic-designers')
        expected_permissions = ('hire', 'fire', 'upload-images')
        self._check_groups_and_permissions(plugin, expected_groups,
                                           expected_permissions)
    
    def test_add_metadata2(self):
        group_fetchers = {'a_nice_group': FakeGroupFetcher2()}
        permission_fetchers = {'global_perms': FakePermissionFetcher3()}
        plugin = AuthorizationMetadata(group_fetchers, permission_fetchers)
        expected_groups = ('webdesigners', 'directors')
        expected_permissions = ('contact', )
        self._check_groups_and_permissions(plugin, expected_groups,
                                           expected_permissions)
    
    def test_add_metadata3(self):
        group_fetchers = {
            'tech-team1': FakeGroupFetcher1(),
            'tech-team2': FakeGroupFetcher2(),
            'executive-team': FakeGroupFetcher3()
            }
        permission_fetchers = {
            'human-resources': FakePermissionFetcher1(),
            'website-management': FakePermissionFetcher2(),
            'gallery-administration': FakePermissionFetcher3()
            }
        plugin = AuthorizationMetadata(group_fetchers, permission_fetchers)
        expected_groups = ('graphic-designers', 'sysadmins', 'webdesigners',
                           'directors')
        expected_permissions = ('view-users', 'edit-users', 'add-users',
                                'hire', 'fire', 'upload-images', 'contact')
        self._check_groups_and_permissions(plugin, expected_groups,
                                           expected_permissions)
    
    def test_add_metadata4(self):
        group_fetchers = {
            'group1': FakeGroupFetcher1(),
            'group2': FakeGroupFetcher2(),
            'group3': FakeGroupFetcher3()
            }
        permission_fetchers = {'my_perms': FakePermissionFetcher3()}
        plugin = AuthorizationMetadata(group_fetchers, permission_fetchers)
        expected_groups = ('graphic-designers', 'sysadmins', 'webdesigners',
                           'directors')
        expected_permissions = ('contact', )
        self._check_groups_and_permissions(plugin, expected_groups,
                                           expected_permissions)
    
    def test_add_metadata5(self):
        group_fetchers = {'my_group': FakeGroupFetcher2()}
        permission_fetchers = {'my_perm': FakePermissionFetcher3()}
        plugin = AuthorizationMetadata(group_fetchers, permission_fetchers)
        expected_groups = ('webdesigners', 'directors')
        expected_permissions = ('contact', )
        self._check_groups_and_permissions(plugin, expected_groups,
                                           expected_permissions)

#}
