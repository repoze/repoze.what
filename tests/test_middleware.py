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

"""
Tests for the repoze.what middleware.

"""

import unittest, os, logging

from zope.interface.verify import verifyClass
from repoze.who.middleware import PluggableAuthenticationMiddleware
from repoze.who.classifiers import default_challenge_decider, \
                                   default_request_classifier
from repoze.who.interfaces import IAuthenticator, IMetadataProvider
from repoze.who.plugins.form import RedirectingFormPlugin
from repoze.who.plugins.auth_tkt import AuthTktCookiePlugin
from repoze.who.plugins.basicauth import BasicAuthPlugin
from repoze.who.plugins.testutil import AuthenticationForgerPlugin, \
                                        AuthenticationForgerMiddleware

from repoze.what.middleware import AuthorizationMetadata, setup_auth

from base import FakeAuthenticator, FakeGroupSourceAdapter, \
                 FakePermissionSourceAdapter, FakeLogger


#{ Fake adapters/plugins


class FakeGroupFetcher1(object):
    def find_sections(self, credentials):
        return ('directors', 'sysadmins')


class FakeGroupFetcher2(object):
    def find_sections(self, credentials):
        return ('webdesigners', 'directors')


class FakeGroupFetcher3(object):
    def find_sections(self, credentials):
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


class TestAuthorizationMetadata(unittest.TestCase):
    """Tests for the ``AuthorizationMetadata`` IMetadata plugin.
    
    All of these tests, except the first one, check the behavior of the plugin
    with random groups and permission fetchers.
    
    """
    
    def _check_groups_and_permissions(self, environ, identity, expected_groups,
                                      expected_permissions):
        # Using sets to forget about order:
        self.assertEqual(set(identity['groups']), set(expected_groups))
        self.assertEqual(set(identity['permissions']),
                         set(expected_permissions))
        # Ensure the repoze.what.credentials environ key is set:
        assert 'repoze.what.credentials' in environ, \
               'The repoze.what credentials were not set'
        credentials = environ['repoze.what.credentials']
        self.assertEqual(set(credentials['groups']), set(expected_groups))
        self.assertEqual(set(credentials['permissions']),
                         set(expected_permissions))

    def test_implements(self):
        verifyClass(IMetadataProvider, AuthorizationMetadata, tentative=True)
    
    def test_adapters_are_loaded_into_environ(self):
        """The available adapters must be loaded into the WSGI environ"""
        environ = {}
        identity = {'repoze.who.userid': 'someone'}
        group_adapters = {
            'tech-team': FakeGroupFetcher1(),
            'executive': FakeGroupFetcher3()
            }
        permission_adapters = {'perms1': FakePermissionFetcher2()}
        plugin = AuthorizationMetadata(group_adapters, permission_adapters)
        plugin.add_metadata(environ, identity)
        # Testing it:
        adapters = {
            'groups': group_adapters,
            'permissions': permission_adapters
            }
        self.assertEqual(adapters, environ.get('repoze.what.adapters'))
    
    def test_userid_in_credentials(self):
        """The userid must also be set in the credentials dict"""
        # For repoze.what 1.X, it's just copied from the repoze.who credentials:
        environ = {}
        identity = {'repoze.who.userid': 'someone'}
        expected_credentials = {
            'repoze.what.userid': 'someone',
            'groups': (),
            'permissions': ()
            }
        plugin = AuthorizationMetadata()
        plugin.add_metadata(environ, identity)
        self.assertEqual(environ['repoze.what.credentials'],
                         expected_credentials)
    
    def test_no_groups_and_permissions(self):
        """Groups/permissions-based authorization is optional"""
        environ = {}
        identity = {'repoze.who.userid': 'whatever'}
        # Configuring the plugin:
        group_adapters = {'executive': FakeGroupFetcher3()}
        permission_adapters = {'perms1': FakePermissionFetcher2()}
        plugin = AuthorizationMetadata()
        plugin.add_metadata(environ, identity)
        # Testing it:
        self._check_groups_and_permissions(environ, identity, (), ())
    
    def test_logger(self):
        # Setting up logging:
        logger = FakeLogger()
        environ = {'repoze.who.logger': logger}
        identity = {'repoze.who.userid': 'whatever'}
        # Configuring the plugin:
        group_adapters = {'executive': FakeGroupFetcher3()}
        permission_adapters = {'perms1': FakePermissionFetcher2()}
        plugin = AuthorizationMetadata(group_adapters, permission_adapters)
        plugin.add_metadata(environ, identity)
        # Testing it:
        messages = "; ".join(logger.messages['info'])
        assert "graphic-designers" in messages
        assert "upload-images" in messages
    
    def test_add_metadata1(self):
        identity = {'repoze.who.userid': 'whatever'}
        environ = {}
        group_adapters = {
            'tech-team': FakeGroupFetcher1(),
            'executive': FakeGroupFetcher3()
            }
        permission_adapters = {'perms1': FakePermissionFetcher2()}
        plugin = AuthorizationMetadata(group_adapters, permission_adapters)
        plugin.add_metadata(environ, identity)
        expected_groups = ('directors', 'sysadmins', 'graphic-designers')
        expected_permissions = ('hire', 'fire', 'upload-images')
        self._check_groups_and_permissions(environ, identity, expected_groups,
                                           expected_permissions)
    
    def test_add_metadata2(self):
        identity = {'repoze.who.userid': 'whatever'}
        environ = {}
        group_adapters = {'a_nice_group': FakeGroupFetcher2()}
        permission_adapters = {'global_perms': FakePermissionFetcher3()}
        plugin = AuthorizationMetadata(group_adapters, permission_adapters)
        plugin.add_metadata(environ, identity)
        expected_groups = ('webdesigners', 'directors')
        expected_permissions = ('contact', )
        self._check_groups_and_permissions(environ, identity, expected_groups,
                                           expected_permissions)
    
    def test_add_metadata3(self):
        identity = {'repoze.who.userid': 'whatever'}
        environ = {}
        group_adapters = {
            'tech-team1': FakeGroupFetcher1(),
            'tech-team2': FakeGroupFetcher2(),
            'executive-team': FakeGroupFetcher3()
            }
        permission_adapters = {
            'human-resources': FakePermissionFetcher1(),
            'website-management': FakePermissionFetcher2(),
            'gallery-administration': FakePermissionFetcher3()
            }
        plugin = AuthorizationMetadata(group_adapters, permission_adapters)
        plugin.add_metadata(environ, identity)
        expected_groups = ('graphic-designers', 'sysadmins', 'webdesigners',
                           'directors')
        expected_permissions = ('view-users', 'edit-users', 'add-users',
                                'hire', 'fire', 'upload-images', 'contact')
        self._check_groups_and_permissions(environ, identity, expected_groups,
                                           expected_permissions)
    
    def test_add_metadata4(self):
        identity = {'repoze.who.userid': 'whatever'}
        environ = {}
        group_adapters = {
            'group1': FakeGroupFetcher1(),
            'group2': FakeGroupFetcher2(),
            'group3': FakeGroupFetcher3()
            }
        permission_adapters = {'my_perms': FakePermissionFetcher3()}
        plugin = AuthorizationMetadata(group_adapters, permission_adapters)
        plugin.add_metadata(environ, identity)
        expected_groups = ('graphic-designers', 'sysadmins', 'webdesigners',
                           'directors')
        expected_permissions = ('contact', )
        self._check_groups_and_permissions(environ, identity, expected_groups,
                                           expected_permissions)
    
    def test_add_metadata5(self):
        identity = {'repoze.who.userid': 'rms'}
        environ = {}
        group_adapters = {'my_group': FakeGroupSourceAdapter()}
        permission_adapters = {'my_perm': FakePermissionSourceAdapter()}
        plugin = AuthorizationMetadata(group_adapters, permission_adapters)
        plugin.add_metadata(environ, identity)
        expected_groups = ('admins', 'developers')
        expected_permissions = ('edit-site', 'commit')
        self._check_groups_and_permissions(environ, identity, expected_groups,
                                           expected_permissions)


class TestSetupAuth(unittest.TestCase):
    """Tests for the setup_auth() function"""
    
    def setUp(self):
        self.old_auth_log = os.environ.get('AUTH_LOG')
        os.environ['AUTH_LOG'] = '0'
    
    def tearDown(self):
        os.environ['AUTH_LOG'] = str(self.old_auth_log)
    
    def _in_registry(self, app, registry_key, registry_type):
        assert registry_key in app.name_registry, ('Key "%s" not in registry' %
                                                   registry_key)
        assert isinstance(app.name_registry[registry_key], registry_type), \
               'Registry key "%s" is of type "%s" (not "%s")' % \
               (registry_key, app.name_registry[registry_key].__class__.__name__,
                registry_type.__name__)
    
    def _makeEnviron(self, kw=None):
        environ = {}
        environ['wsgi.version'] = (1,0)
        if kw is not None:
            environ.update(kw)
        return environ

    
    def _makeApp(self, groups, permissions, **who_args):
        cookie = AuthTktCookiePlugin('secret', 'authtkt')
        
        form = RedirectingFormPlugin('/login', '/login_handler',
                                     '/logout_handler',
                                     rememberer_name='cookie')
        
        identifiers = [('main_identifier', form), ('cookie', cookie)]
        
        authenticators = [('fake_authenticator', FakeAuthenticator())]
        
        challengers = [('form', form)]
        
        if groups is None:
            app_with_auth = setup_auth(
                DummyApp(),
                identifiers=identifiers,
                authenticators=authenticators,
                challengers=challengers,
                **who_args
                )
        else:
            app_with_auth = setup_auth(
                DummyApp(),
                groups,
                permissions,
                identifiers=identifiers,
                authenticators=authenticators,
                challengers=challengers,
                **who_args
                )
        return app_with_auth

    def test_no_extras(self):
        groups = [FakeGroupSourceAdapter()]
        permissions = [FakePermissionSourceAdapter()]
        app = self._makeApp(groups, permissions)
        assert isinstance(app, PluggableAuthenticationMiddleware)
        self._in_registry(app, 'main_identifier', RedirectingFormPlugin)
        self._in_registry(app, 'authorization_md', AuthorizationMetadata)
        self._in_registry(app, 'cookie', AuthTktCookiePlugin)
        self._in_registry(app, 'fake_authenticator', FakeAuthenticator)
        self._in_registry(app, 'form', RedirectingFormPlugin)
        assert isinstance(app.challenge_decider,
                          default_challenge_decider.__class__)
        assert isinstance(app.classifier,
                          default_request_classifier.__class__)
    
    def test_with_auth_log(self):
        os.environ['AUTH_LOG'] = '1'
        groups = [FakeGroupSourceAdapter()]
        permissions = [FakePermissionSourceAdapter()]
        app = self._makeApp(groups, permissions)
    
    def test_no_groups_and_permissions(self):
        """Groups/permissions-based authorization must be optional"""
        groups = None
        permissions = None
        app = self._makeApp(groups, permissions)
        self._in_registry(app, 'authorization_md', AuthorizationMetadata)
        authorization_md = app.name_registry['authorization_md']
        self.assertEqual(authorization_md.group_adapters, None)
        self.assertEqual(authorization_md.permission_adapters, None)

    def test_without_authentication(self):
        groups = [FakeGroupSourceAdapter()]
        permissions = [FakePermissionSourceAdapter()]
        app = self._makeApp(groups, permissions, skip_authentication=True)
        assert isinstance(app, AuthenticationForgerMiddleware)
        self._in_registry(app, 'auth_forger', AuthenticationForgerPlugin)
        self._in_registry(app, 'cookie', AuthTktCookiePlugin)
        assert isinstance(app.challenge_decider,
                          default_challenge_decider.__class__)
        assert isinstance(app.classifier,
                          default_request_classifier.__class__)

class DummyApp:
    environ = None
    def __call__(self, environ, start_response):
        self.environ = environ
        return []


#}
