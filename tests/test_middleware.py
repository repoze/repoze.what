# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007, Agendaless Consulting and Contributors.
# Copyright (c) 2008, Florent Aide <florent.aide@gmail.com>.
# Copyright (c) 2008-2009, Gustavo Narea <me@gustavonarea.net>.
# Copyright (c) 2009, 2degrees Limited <gustavonarea@2degreesnetwork.com>.
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

from StringIO import StringIO
import unittest, os, logging

from webob import Request
from zope.interface.verify import verifyClass
from repoze.who.middleware import PluggableAuthenticationMiddleware
from repoze.who.classifiers import default_challenge_decider, \
                                   default_request_classifier
from repoze.who.interfaces import IMetadataProvider
from repoze.who.plugins.form import RedirectingFormPlugin
from repoze.who.plugins.auth_tkt import AuthTktCookiePlugin
from repoze.who.plugins.testutil import AuthenticationForgerPlugin, \
                                        AuthenticationForgerMiddleware

from repoze.what.middleware import (AuthorizationMiddleware,
    AuthorizationMetadata, setup_auth, setup_request, _Credentials,
    forge_request)

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


#{ Miscellaneous mock objects


class MockApp(object):
    """Mock WSGI application."""
    
    environ = None
    
    def __call__(self, environ, start_response):
        self.environ = environ
        return []


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
            'groups': set(),
            'permissions': set(),
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


class TestAuthorizationMiddleware(unittest.TestCase):
    """Tests for the AuthorizationMiddleware middleware."""
    
    def test_only_app(self):
        mw = AuthorizationMiddleware(MockApp())


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
                MockApp(),
                identifiers=identifiers,
                authenticators=authenticators,
                challengers=challengers,
                **who_args
                )
        else:
            app_with_auth = setup_auth(
                MockApp(),
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
        assert isinstance(app.logger, logging.Logger)
    
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
        assert isinstance(app.logger, logging.Logger)


class TestSettingUpRequest(unittest.TestCase):
    """Tests for the setup_request() function."""
    
    def test_no_userid_and_no_adapters(self):
        environ = {}
        req = setup_request(environ, None, None, None)
        assert len(req.environ) >= 4
        assert "repoze.what.positional_args" in req.environ
        assert "repoze.what.named_args" in req.environ
        # Checking the credentials:
        assert len(req.environ['repoze.what.credentials']) == 3
        assert req.environ['repoze.what.credentials']['repoze.what.userid'] is None
        assert len(req.environ['repoze.what.credentials']['groups']) == 0
        assert len(req.environ['repoze.what.credentials']['permissions']) == 0
        # Checking the adapters:
        assert len(req.environ['repoze.what.adapters']) == 2
        assert req.environ['repoze.what.adapters']['groups'] is None
        assert req.environ['repoze.what.adapters']['permissions'] is None
    
    def test_with_userid_and_adapters(self):
        group_adapters = {'my_group': FakeGroupSourceAdapter()}
        permission_adapters = {'my_perm': FakePermissionSourceAdapter()}
        environ = {}
        req = setup_request(environ, "rms", group_adapters, permission_adapters)
        assert len(req.environ) >= 4
        assert "repoze.what.positional_args" in req.environ
        assert "repoze.what.named_args" in req.environ
        # Checking the credentials:
        assert len(req.environ['repoze.what.credentials']) == 3
        assert req.environ['repoze.what.credentials']['repoze.what.userid'] == "rms"
        assert len(req.environ['repoze.what.credentials']['groups']) == 2
        assert len(req.environ['repoze.what.credentials']['permissions']) == 2
        # Checking the adapters:
        assert len(req.environ['repoze.what.adapters']) == 2
        assert req.environ['repoze.what.adapters']['groups'] is group_adapters
        assert req.environ['repoze.what.adapters']['permissions'] is permission_adapters
    
    def test_with_get_arguments(self):
        # Forging the GET params:
        environ = Request.blank("/blog/view.php?id=3&session=ABC123").environ
        req = setup_request(environ, None, None, None)
        assert req.environ['repoze.what.positional_args'] == 0
        assert req.environ['repoze.what.named_args'] == set(["id", "session"])
    
    def test_with_post_arguments(self):
        # Forging the POST params:
        mock_req = Request.blank("/blog/view-post.php")
        mock_req.method = "POST"
        mock_req.body = "id=3&session=ABC123"
        # Testing it:
        environ = mock_req.environ
        req = setup_request(environ, None, None, None)
        assert req.environ['repoze.what.positional_args'] == 0
        assert req.environ['repoze.what.named_args'] == set(["id", "session"])
    
    def test_named_arguments(self):
        environ = {
            'wsgiorg.routing_args': ((), {'foo': "bar", 'baz': "foo"}),
        }
        req = setup_request(environ, None, None, None)
        assert req.environ['repoze.what.positional_args'] == 0
        assert req.environ['repoze.what.named_args'] == set(["foo", "baz"])
    
    def test_with_named_positional_post_and_get_arguments(self):
        # Forging all the params:
        mock_req = Request.blank("/blog/view-post.php?foo=bar")
        mock_req.method = "POST"
        mock_req.body = "id=3&session=ABC123"
        mock_req.environ['wsgiorg.routing_args'] = (
            ("a", "b", "c", "1", "2", "3"),
            {'baz': "bar"}
            )
        # Testing it:
        environ = mock_req.environ
        req = setup_request(environ, None, None, None)
        assert req.environ['repoze.what.positional_args'] == 6
        assert req.environ['repoze.what.named_args'] == set(["id", "session",
                                                             "foo", "baz"])
    
    def test_with_positional_args(self):
        environ = {
            'wsgiorg.routing_args': (("foo", "bar", "baz"), {}),
        }
        req = setup_request(environ, None, None, None)
        assert req.environ['repoze.what.positional_args'] == 3
        assert req.environ['repoze.what.named_args'] == set()
    
    def test_request_copy(self):
        """
        A clear copy of the environ must be set in the environment, so it won't
        have to be built many times to verify authorization.
        
        """
        # Checking with a GET request:
        environ1 = {
            'SCRIPT_NAME': "/trac",
            'PATH_INFO': "/wiki",
            'REQUEST_METHOD': "GET",
            'QUERY_STRING': "var=val",
            }
        req1 = setup_request(environ1, None, None, None)
        assert "repoze.what.clear_request" in req1.environ
        clear_request1 = req1.environ['repoze.what.clear_request']
        assert clear_request1.script_name == "/trac"
        assert clear_request1.path_info == "/wiki"
        assert clear_request1.method == "GET"
        assert len(clear_request1.GET) == 0
        # Checking with a POST request:
        environ2 = {
            'SCRIPT_NAME': "/trac",
            'PATH_INFO': "/wiki",
            'REQUEST_METHOD': "POST",
            'CONTENT_LENGTH': "7",
            'wsgi.input': StringIO("var=val"),
            }
        req2 = setup_request(environ2, None, None, None)
        assert "repoze.what.clear_request" in req2.environ
        clear_request2 = req2.environ['repoze.what.clear_request']
        assert clear_request2.script_name == "/trac"
        assert clear_request2.path_info == "/wiki"
        assert clear_request2.method == "GET"
        assert len(clear_request2.GET) == 0
        assert len(clear_request2.POST) == 0
        # Checking with a POST request and a query string:
        environ3 = {
            'SCRIPT_NAME': "/trac",
            'PATH_INFO': "/wiki",
            'REQUEST_METHOD': "POST",
            'CONTENT_LENGTH': "7",
            'QUERY_STRING': "foo=bar",
            'wsgi.input': StringIO("var=val"),
            }
        req3 = setup_request(environ3, None, None, None)
        assert "repoze.what.clear_request" in req3.environ
        clear_request3 = req3.environ['repoze.what.clear_request']
        assert clear_request3.script_name == "/trac"
        assert clear_request3.path_info == "/wiki"
        assert clear_request3.method == "GET"
        assert len(clear_request3.GET) == 0
        assert len(clear_request3.POST) == 0


class TestForgingRequests(unittest.TestCase):
    """Tests for the forge_request() function."""
    
    def setUp(self):
        req = Request.blank("/this/is/the/path_info")
        req = setup_request(req.environ, None, None, None)
        self.original_environ = req.environ
    
    def test_original_clear_request_is_not_modified(self):
        forge_request(self.original_environ, "/somewhere", (), {})
        original_clear_req = self.original_environ['repoze.what.clear_request']
        assert original_clear_req.path_info == "/this/is/the/path_info"
    
    def test_with_no_query_string(self):
        forged_req = forge_request(
            self.original_environ,
            "/path",
            ("arg1", "arg2"),
            {'name': "value"},
            )
        assert forged_req.path_info == "/path"
        assert forged_req.query_string == ""
        assert forged_req.urlargs == ("arg1", "arg2")
        assert forged_req.urlvars == dict(name="value")
    
    def test_with_query_string(self):
        forged_req = forge_request(
            self.original_environ,
            "/path?var1=val1&var2=val2",
            ("argA", ),
            {'name': "val"},
            )
        assert forged_req.path_info == "/path"
        assert forged_req.query_string == "var1=val1&var2=val2"
        assert forged_req.urlargs == ("argA", )
        assert forged_req.urlvars == dict(name="val")


class TestCredentials(unittest.TestCase):
    """Tests for the repoze.what credentials dict."""
    
    def test_constructor(self):
        # Setup:
        group_adapters = object()
        permission_adapters = object()
        credentials = _Credentials("foo", group_adapters, permission_adapters)
        # Tests:
        assert len(credentials) == 3
        assert credentials['repoze.what.userid'] == "foo"
        assert "groups" in credentials
        assert "permissions" in credentials
        assert not credentials._groups_loaded
        assert not credentials._permissions_loaded
    
    def test_setting_groups_and_permissions(self):
        # Setup:
        group_adapters = object()
        permission_adapters = object()
        credentials = _Credentials("foo", group_adapters, permission_adapters)
        # Tests:
        groups = ("g1", "g2", "g3")
        permissions = ("p1", "p2")
        credentials['groups'] = groups
        credentials['permissions'] = permissions
        assert credentials._groups_loaded
        assert credentials._permissions_loaded
    
    def test_getting_groups_and_permissions(self):
        group_adapters = {'my_group': FakeGroupSourceAdapter()}
        permission_adapters = {'my_perm': FakePermissionSourceAdapter()}
        credentials = _Credentials("rms", group_adapters, permission_adapters)
        assert credentials['groups'] == set(["admins", "developers"])
        assert credentials['permissions'] == set(["edit-site", "commit"])
        assert credentials._groups_loaded
        assert credentials._permissions_loaded
    
    def test_getting_groups_and_permissions_for_non_existing_user(self):
        credentials = _Credentials("foo", None, None)
        assert credentials['groups'] == set()
        assert credentials['permissions'] == set()
        assert credentials._groups_loaded
        assert credentials._permissions_loaded


#}
