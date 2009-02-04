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
Tests for the :mod:`repoze.what` credentials handling.

"""

from unittest import TestCase

from repoze.what.credentials import BaseCredentialProvider, Credentials
from repoze.what.patterns.groups import GroupCredentialsProvider

from base import FakeLogger


#{ The tests themselves


class TestCredentials(TestCase):
    def test_repr(self):
        c = Credentials()
        assert 'repoze.what credentials (hidden, dict-like)' in repr(c)
        assert 'repoze.what credentials (hidden, dict-like)' in str(c)
        assert 'repoze.what credentials (hidden, dict-like)' in unicode(c)


class TestBaseCredentialProvider(TestCase):
    """Tests for the ``BaseCredentialProvider`` base class."""
    
    def test_it(self):
        provider = BaseCredentialProvider()
        self.assertRaises(NotImplementedError, provider.load_credentials, {},
                          {})
        self.assertEqual(None, provider.credentials_loaded)
        try:
            provider.provider_name
            self.fail('The .provider_name attribute must not be set')
        except NotImplementedError:
            pass


class TestGroupCredentialsProvider(TestCase):
    """
    Tests for the ``GroupCredentialsProvider`` credentials provider plugin.
    
    """
    
    def test_provider_name(self):
        group_adapters = {
            'tech-team': FakeGroupFetcher2(),
            'executive': FakeGroupFetcher1()
            }
        provider = GroupCredentialsProvider(group_adapters)
        self.assertEqual(provider.provider_name, 'group')
    
    def test_credentials_provided(self):
        group_adapters = {
            'tech-team': FakeGroupFetcher2(),
            'executive': FakeGroupFetcher1()
            }
        provider = GroupCredentialsProvider(group_adapters)
        self.assertEqual(provider.credentials_loaded, 
                         ['groups', 'permissions'])
    
    def test_adapters_are_loaded_into_environ(self):
        """The available adapters must be loaded into the WSGI environ"""
        environ = {}
        credentials = {'repoze.what.userid': 'someone'}
        group_adapters = {
            'tech-team': FakeGroupFetcher2(),
            'executive': FakeGroupFetcher1()
            }
        permission_adapters = {'perms1': FakePermissionFetcher2()}
        plugin = GroupCredentialsProvider(group_adapters, permission_adapters)
        plugin.load_credentials(environ, credentials)
        # Testing it:
        adapters = {
            'groups': group_adapters,
            'permissions': permission_adapters
            }
        self.assertEqual(adapters, environ['repoze.what.adapters'])
    
    def test_logger(self):
        # Setting up logging:
        logger = FakeLogger()
        environ = {'repoze.what.logger': logger}
        credentials = {'repoze.what.userid': 'whatever'}
        # Configuring the plugin:
        group_adapters = {'executive': FakeGroupFetcher1()}
        permission_adapters = {'perms1': FakePermissionFetcher2()}
        plugin = GroupCredentialsProvider(group_adapters, permission_adapters)
        plugin.load_credentials(environ, credentials)
        # Testing it:
        messages = "; ".join(logger.messages['info'])
        assert "directors" in messages
        assert "sysadmins" in messages
        assert "hire" in messages
        assert "fire" in messages
    
    def test_load_credentials_with_no_permissions(self):
        """Groups may not have permissions granted"""
        environ = {}
        credentials = {'repoze.what.userid': 'whatever'}
        # Configuring the plugin:
        group_adapters = {'executive': FakeGroupFetcher1(),}
        plugin = GroupCredentialsProvider(group_adapters)
        plugin.load_credentials(environ, credentials)
        # Testing it:
        expected_groups = ('directors', 'sysadmins')
        self._check_groups_and_permissions(environ, credentials, 
                                           expected_groups, ())
    
    def test_load_credentials_with_groups_and_permissions(self):
        credentials = {'repoze.what.userid': 'whatever'}
        environ = {}
        group_adapters = {
            'executive': FakeGroupFetcher1(),
            'tech-team': FakeGroupFetcher2()
            }
        permission_adapters = {
            'perms1': FakePermissionFetcher1(),
            'perms2': FakePermissionFetcher2(),
            }
        plugin = GroupCredentialsProvider(group_adapters, permission_adapters)
        plugin.load_credentials(environ, credentials)
        expected_groups = ('directors', 'sysadmins', 'webdesigners')
        expected_permissions = ('hire', 'fire', 'view-users', 'add-users',
                                'edit-users')
        self._check_groups_and_permissions(environ, credentials, 
                                           expected_groups,
                                           expected_permissions)
    
    def _check_groups_and_permissions(self, environ, credentials,
                                      expected_groups, expected_permissions):
        # Using sets to forget about order:
        self.assertEqual(set(credentials['groups']), set(expected_groups))
        self.assertEqual(set(credentials['permissions']),
                         set(expected_permissions))


#{ Fake adapters/plugins


class FakeGroupFetcher1(object):
    def find_sections(self, credentials):
        return ('directors', 'sysadmins')


class FakeGroupFetcher2(object):
    def find_sections(self, credentials):
        return ('webdesigners', 'directors')


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


#}
