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

"""Test suite for the quickstart module."""

import unittest

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from repoze.what.quickstart import SQLAuthenticatorPlugin, \
                                           find_plugin_translations

from base import FakeGroupSourceAdapter, FakePermissionSourceAdapter, \
                 FakeAuthenticator
import databasesetup

databasesetup.setup_database()


class TestTranslationsFinder(unittest.TestCase):
    def setUp(self):
        self.finder = find_plugin_translations
        self.base = {
            'group_adapter': {},
            'permission_adapter': {},
            'authenticator': {}}
    
    def test_no_translations(self):
        self.assertEqual(self.finder(), self.base)
    
    def test_all_translations(self):
        translations = {
            'validate_password': 'check_passwd',
            'user_name': 'member_name',
            'users': 'members',
            'group_name': 'team_name',
            'groups': 'teams',
            'permission_name': 'authorization_name',
            'permissions': 'authorizations'
        }
        self.base['group_adapter'] = {
            'section_name': translations['group_name'],
            'sections': translations['groups'],
            'item_name': translations['user_name'],
            'items': translations['users']
            }
        self.base['permission_adapter'] = {
            'section_name': translations['permission_name'],
            'sections': translations['permissions'],
            'item_name': translations['group_name'],
            'items': translations['groups']
            }
        self.base['authenticator'] = {
            'user_name': translations['user_name'],
            'validate_password': translations['validate_password']
            }
        self.assertEqual(self.finder(translations), self.base)
    
    def test_setting_a_random_translation(self):
        translations = {'user_name': 'member_name'}
        self.base['group_adapter']['item_name'] = translations['user_name']
        self.base['authenticator']['user_name'] = translations['user_name']
        self.assertEqual(self.finder(translations), self.base)


class TestSQLAuthenticatorPlugin(unittest.TestCase):

    def _makeOne(self, user, has_multiple_results=False):
        user_class = databasesetup.User
        user_query = UserQuery(user, has_multiple_results)
        session_factory = DummySessionFactory(user_query)
        plugin = SQLAuthenticatorPlugin(user_class, session_factory)
        return plugin

    def _makeEnviron(self, kw=None):
        environ = {}
        environ['wsgi.version'] = (1,0)
        if kw is not None:
            environ.update(kw)
        return environ

    def test_implements(self):
        from zope.interface.verify import verifyClass
        from repoze.who.interfaces import IAuthenticator
        verifyClass(IAuthenticator, SQLAuthenticatorPlugin, tentative=True)

    def test_authenticate_noresults(self):
        user = None
        plugin = self._makeOne(user)
        environ = self._makeEnviron()
        identity = {'login':'foo', 'password':'bar'}
        result = plugin.authenticate(environ, identity)
        self.assertEqual(result, None)

    def test_authenticate_comparefail(self):
        user = DummyUser(False)
        plugin = self._makeOne(user)
        environ = self._makeEnviron()
        identity = {'login':'fred', 'password':'bar'}
        result = plugin.authenticate(environ, identity)
        self.assertEqual(result, None)

    def test_authenticate_comparesuccess(self):
        user = DummyUser(True)
        environ = self._makeEnviron()
        plugin = self._makeOne(user)
        identity = {'login':'fred', 'password':'bar'}
        result = plugin.authenticate(environ, identity)
        self.assertEqual(result, u'myusername')

    def test_authenticate_nologin(self):
        user = DummyUser(True)
        environ = self._makeEnviron()
        plugin = self._makeOne(user)
        environ = self._makeEnviron()
        identity = {}
        result = plugin.authenticate(environ, identity)
        self.assertEqual(result, None)

    def test_authenticate_multiple_results(self):
        user = DummyUser(True)
        environ = self._makeEnviron()
        plugin = self._makeOne(user, True)
        identity = {'login':'fred', 'password':'bar'}
        result = plugin.authenticate(environ, identity)
        self.assertEqual(result, None)


class TestMakeWhoMiddleware(unittest.TestCase):
    def _getFUT(self):
        from repoze.what.quickstart import setup_sql_auth
        return setup_sql_auth

    def test_it(self):
        # just test that it doesnt blow up
        groups_adapters = (FakeGroupSourceAdapter(), )
        permissions_adapters = (FakePermissionSourceAdapter(), )
        authenticators = (('auth', FakeAuthenticator()), )
        config = {}
        app = DummyApp()
        func = self._getFUT()
        mw = func(app, config, databasesetup.User, databasesetup.Group,
                  databasesetup.Permission, databasesetup.DBSession)
        self.assertEqual(mw.app, app)
        
        
class DummyApp:
    pass


class DummyGroup:
    def __init__(self, name):
        self.group_name = name


class DummyPermission:
    def __init__(self, name):
        self.permission_name = name
        
        
class DummyUser:
    user_name = u'myusername'
    groups = (DummyGroup('g1'), DummyGroup('g2'))
    permissions = (DummyPermission('p1'), DummyPermission('p2'))
    
    def __init__(self, result=True):
        self.result = result

    def validate_password(self, pwd):
        return self.result


class UserQuery:
    def __init__(self, user, has_multiple_results):
        self.user = user
        self.has_multiple_results = has_multiple_results
    def filter(self, expr):
        return self
    def first(self):
        return self.user
    def one(self):
        if self.user is None:
            raise NoResultFound
        if self.has_multiple_results:
            raise MultipleResultsFound
        return self.user
    def get(self, id):
        return self.user


class DummySessionFactory:
    def __init__(self, uquery):
        self.uquery = uquery
    def __call__(self):
        return self
    def query(self, klass):
        return self.uquery
